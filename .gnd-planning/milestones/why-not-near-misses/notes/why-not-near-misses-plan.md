# Near-miss values in why-not, and a disclosure mode

r3, 2026-11-01. **Approved by the owner `(a1)`.** Milestone:
`why-not-near-misses`.
Source: [gnd-public issue #70](https://github.com/vasiloglou/gnd-public/issues/70)
(request GR-T8 in the reporter's numbering), plus the owner's directions of
2026-11-01.
Inspection baseline: `33c260e` (main after PR #69).
Plan approved `(a1)`. Phase execution, implementation and publication have not
occurred; each phase spec has its own owner gate.

**Revision history and tags.**

- **r1:** first draft (including NM4, added before review). Reviewed in plan
  review round 1 (four local readers) as SHA-256
  `ec9cea0eb204934a8cd390410bed31750312eb2db369bee186353ecdc6e5db63` (NM1 spec
  `e3855ca569e890a994f015b64f5c64c651f2416f7b4e7b499ec529737913b670`); see the
  [round-1 disposition](plan-review-r1-disposition.md).
- **`(o1)` 2026-11-01:** quoted: "Except for 1 I think you should go with your
  recommendations. For 1 I think we need a general mode flag. when gnd works in a
  safe environment meaning it is behind the public interface it should not
  redact. But when it is facing a customer it should." The recommendations were
  given in session on five design questions; `(o1)` covers NM-D1 (item 1,
  answered by the mode) and the recommended answers NM-D3, D4 and D5. It does not
  cover NM-D2 or NM-D6, on which no recommendation had been given. (p1-I)
- **`(o2)` 2026-11-01:** asked "four local readers or the six-seat panel?" with
  four local readers offered first, the owner replied, quoted: "yes I also want
  you to add a plan to update the documentation". Read as selecting four local
  readers (NM-D9, provisional until confirmed at the plan gate) and as the
  requirement for NM4. (p1-I)
- **`(p1)` r2, 2026-11-01:** asked "Should I apply all the proposed answers as
  revision r2 and run a confirmation round on the blocking problems? Or would
  you rather choose differently on any of the four?", the owner replied, quoted:
  "yes". Read as accepting the round-1 repair themes A-Q and the proposed
  answers to the four owner decisions: E (a), C (truncate), B (search off on the
  public path until NM3), G (unchanged in every mode). Theme letters are cited
  as `(p1-A)` and so on.
- **r2:** reviewed in the confirmation round (round 2, the same four lenses) as
  SHA-256 `211d9e018febdbcc4c2a76ebbb43fce631532fd3af8953f88694793490a665de`
  (NM1 spec `1b739a57ce49f7418936dabd82113a7f35579301c73015bef6a04a5087de1d72`);
  all four readers approve with fixes; self-inflicted ratio 0.82, so the stop
  rule ends review. See the [round-2 disposition](plan-review-r2-disposition.md).
- **`(p2)` r3, 2026-11-01:** asked "Should I write r3 with all of these fixes and
  no further review round, then hand you the plan-approval decision? Or would
  you rather I run a third review round over r3?", after a summary proposing to
  pass only `customer` to child processes and to keep the redacted near-miss
  count with the membership signal documented, the owner replied, quoted: "Yes,
  write r3". Read as accepting the round-2 repair themes R-AA with their
  proposed answers (rulings NM-D16, NM-D17) and no further review round. Theme
  letters are cited as `(p2-R)` and so on. **Sentences marked `(p2)` carry no
  review opinion**; the owner decides plan approval over these bytes.

- **`(a1)` plan approval, 2026-11-01:** asked "Do you approve plan r3,
  including the proposed decisions?", the owner replied, quoted: "Approve the
  plan". Approved subject: this plan's r3 bytes, SHA-256
  `4afc28774fd14ddc1be8d7ce6d6d20e6ab120b11ecc128db4562fc608d12e745` before this tag was added (the only later edits are this tag, the status
  lines and the §10 ruling column). Read as ruling the proposed decisions NM-D2,
  D6, D7, D8, D10, D11 as proposed and confirming NM-D9 (a). It approves no
  phase spec; the NM1 spec r3 awaits its own gate.

A direction on design questions is not approval of the plan.

## Problem and completion predicates

`gnd why-not` names the first step of a clause that left no bindings and up to
five bindings that reached it. When that step is a positive atom, nothing says
what the atom's fact type *does* hold. A join that is empty because one side
spells an entity `ACME CORP.` and the other `Acme Corp.` reads the same as a
join with nothing to meet. The reporter's deletion test localized all 30 gaps
where the missing fact was simply absent, but only 2 of 4 where bound values
existed on both sides and failed to meet; one real failure (an entity name
re-extracted in capitals) was found only by reading a dump.

**What the issue asks for.** A diagnostic, not a change of meaning: for an empty
join, report the join variables and a few values from each side that differ only
by case, whitespace or punctuation. GND keeps exact matching; deciding that two
spellings name one entity stays the caller's job.

**What the owner added `(o1)`.** Near-miss values are population values, so
they fall under redaction. Today GND has two redaction conventions and no
deployment-level switch:

- **Declared redaction** (`src/gnd/redaction.py`): roles a model declares
  `redact: true` are projected out of check-family outputs (13 `OutputKind`s).
  Applied by default in the API and the CLI; `unredacted=True` or the hidden flag
  `--unredacted` (`commands/_arguments.py:60`, 6 parsers, plus
  `judgments.py:15`) retains values. Every other population value (issue
  messages, witnesses of undeclared roles) is emitted in every mode. No packaged
  example declares `redact: true`. (p1-E)
- **View redaction** (witness lane): `api.witness` and `api.why_not` return raw
  values; the CLI views `witness`, `witness-view`, `replay`, `why-not` show no
  population values unless `--raw` (`witness/cli.py:18-40`). The `lean`,
  `souffle`, `souffle-run` and `souffle-witness` exports take `--raw`
  (`export/lean_cli.py:18`, `souffle_cli.py:18-19`) and their Python functions
  take `raw=` (`export/service.py:5,21,33,64`; re-exported in `api.py:68-88`).
  (p1-F)

Some outputs print population values with no flag at all: `gnd fidelity` quotes
an extracted fact verbatim (`fidelity/report.py:202,223`) and ILP export writes
undeclared values into its prompt (`export/ilp.py:11-13`). (p2-T)

No environment variable or configuration file selects either convention today.
An operator running GND behind their own interface has to pass a raw flag on
every call; an operator exposing GND to customers cannot stop a caller from
passing one.

**Outcome.**

1. Each atom blocker in a why-not payload carries a bounded, deterministic
   near-miss report: rows of the blocker's fact type that production could have
   matched except that bound string values differ, and that agree once strings
   are compared after a fixed normalization. Matching stays exact; statuses,
   blockers, counts, `work` and exits are unchanged. (p1-A, p1-C)
2. One disclosure mode, set by the operator, decides whether GND emits
   population values: `internal` emits them; `customer` withholds declared-role
   values in the check family and every population value in witness-lane,
   `lean` and `souffle*` outputs, and refuses every raw request those surfaces
   accept. A fixed list of outputs is unchanged in every mode and documented as
   such. (p1-E, p2-V)

The milestone can close when:

1. On every corpus case, the kernel's near-miss report equals an independent
   oracle's when untruncated, the generated corpus produces non-empty reports
   above a recorded floor, a lowered-cap pass keeps every truncated report
   within the oracle's (count ≤, pairs ⊆), the exactness invariant holds, and
   with the search off every existing golden and test is unchanged (NM1).
   (p1-A, p1-B, p1-P, p2-X)
2. The near-miss search has its own inspection cap that truncates and never
   fails a request; at default limits the cap cannot be reached (inspections ≤
   `work.probes` ≤ 200,000), so it guards lowered limits, and counter tests
   with literal values fix the truncation point under lowered caps (NM1).
   (p1-C, p2-X)
3. Every root-parser leaf and every public callable of `gnd.api`, its classes
   and `gnd.export.service` has a disclosure row (*site*, *value-free*, or
   *emits values in every mode*), and every row resolves to live code (NM2-C2).
   On every site `customer` withholds the values its convention covers and
   refuses raw requests; `internal` returns raw values; with the mode unset
   every disclosure decision is as at `33c260e`; an ambient environment value
   cannot change the parity gates; child processes receive only `customer`
   (NM2). (p1-E, p1-F, p1-J, p1-M, p2-R, p2-T)
4. `gnd why-not` and `gnd.api.why_not` expose near-misses under
   `gnd-why-not/2`; the schema ties `near_misses` to `"redacted"` in the
   redacted view; `docs/reference/why-not.md` holds the normative near-miss
   section; the spelling-gap how-to section runs (NM3). (p1-H, p1-N)
5. Every page and packaged skill reference describing redaction, raw values or
   why-not output has a recorded disposition; new pages are registered with the
   docs runner and execute; docs gates exit 0; the owner has seen the
   checkpoints (NM4). (p1-O)
6. Focused gates, independent diff reviews, the question sweep and a PR are
   recorded. Owner acceptance is separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| NM-R1: Exact matching stays the meaning | Near-misses never change a status, blocker, count, `work` counter, exit, extension or any `check`/`witness` payload. Normalization only *finds* candidates; join, identity, negation and comparisons keep the production helpers. A near-miss pair whose rows match exactly is an internal defect. The search is not charged to the walk's shared ceilings, so it cannot cause a `work-limit` exit. (p1-C) |
| NM-R2: One fixed normalization, one home | One function, one normative definition (the NM1 spec, then `docs/reference/why-not.md` from NM3). No fuzzy, edit-distance or locale-dependent matching. It uses the running interpreter's Unicode database; this is stated in the normative text. Non-string values never near-match. (p1-Q) |
| NM-R3: Bounded, counted, deterministic | The search inspects every row of the fact type plus every binding once, counts pairs per normalized key instead of enumerating them, and builds at most 25 pairs per key, of which 5 are reported. Its own inspection counter has a fixed cap; reaching it sets `near_miss_truncated` and stops the search. Inspections never exceed the probes the blocker's join already charged, so the default cap is defence in depth. Output order is canonical. Tests assert counters, not wall time. (p1-C, p2-X, p2-Y) |
| NM-R4: Disclosure is decided once, after the verdict | The mode is resolved at the public boundary by one resolver in `gnd.disclosure`, its runtime home: the CLI sets a context variable for the invocation and resets it on exit; `gnd.api` functions read it and the environment, and `customer` from either source wins. Never resolved in the checker, evaluator or why-not kernel. The site table is the coverage test over that resolver (standing rule 4). (p1-D, p2-S, p2-T) |
| NM-R5: Unset keeps today's disclosure | With no mode set, every disclosure decision (what is redacted, what raw requests do) and every child environment is as at `33c260e`. Exceptions, enumerated and released: the why-not `/2` payload (NM3) and the root help/usage text and RF1 goldens listing the new option (NM2). (p1-J) |
| NM-R6: Customer mode is a lock, with a stated threat model | In `customer` mode every raw request is refused, not downgraded, and the CLI option can only tighten the mode. Protected party: end users whose requests an operator-controlled wrapper forwards into GND's CLI arguments or `gnd.api` keywords. For code running inside the GND process the mode is a guard, not a lock: such code can change any library setting, and the docs say so. In customer mode the redacted near-miss count tells a caller who supplied `--row` values whether a spelling variant of them exists; `disclosure.md` names this signal. (p1-D, p2-W) |
| NM-R7: Layering and query policy | New code joins existing homes in `tools/gnd_layers.json` (`gnd.disclosure` beside `gnd.redaction` in `checking`) with zero new allowances; lower layers (for example `gnd.agents`, infrastructure) receive the mode as a parameter, never import the resolver; model reads follow WN-R7; the RF6 allow-list gains no row. (p2-R) |
| NM-R8: Approval, evidence, anonymity | `auto=false`. Plan authorship is not approval. Downstream applications are not named in committed artifacts; `tests/test_why_not_anonymity.py` scans files added since `33c260e`. |

Each phase spec binds every rule above and every rule in
`.codex/skills/process-phase/references/standing-rules.md`, by name or with a
one-sentence argument that it does not apply.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issue #70 | Request, use case, example shape |
| Owner directions `(o1)`, `(o2)`, `(p1)`, `(p2)`, `(a1)` | Mode; rulings NM-D1..D17 |
| `src/gnd/witness/why_not.py` (`_join`, `_candidates`, `_atom_blocker`, `_samples`, `_Budget`, `WhyNotLimits`), `src/gnd/extensions.py:629-680` (`_joined_atom_candidates` per-row checks) | Where near-misses attach; which rows production could match |
| `src/gnd/witness/view.py`, `witness/cli.py`, `witness/service.py`, `src/gnd/why-not.schema.json` | Why-not views, flags, schema (already ties `view: redacted` to redacted fields; WN2-R1 was fixed in WN2) (p1-H) |
| Disclosure surfaces (classified in NM2-C2): every leaf of the root parser; `gnd.api` module-level callables (including `judgments`, outside `__all__`), its classes, `gnd.export.service`; `redaction.py` and `emitter_specs()` (12 kinds; `admission` added by hand) | Every place a mode could apply or that emits values in every mode (p1-F, p2-T) |
| `src/gnd/api.py:109-118` (witness-lane identity aliases), `witness/cli.py:46-81`, `commands/checking.py:34` (`api._run_*`) | Projection points (p2-U) |
| Spawners: callers of `run_bounded_process`, `subprocess.Popen`, `subprocess.run` and `create_subprocess_exec` in `src/gnd` (13 modules at `33c260e`, among them `solve.py`, `agents.py` `_private_environment`, `exp/adapter_policy.py:303-312`, `exp/session.py`, `declared_adapter.py`, `review/adapters.py`, `exp/tests_runner.py`); `exp/session_environment.py` `verifier_environment()` | Child processes and which ones may receive the mode (p1-L, p2-R) |
| `discover/candidates.py:131-132` (owner ruling 2026-10-25: redacted roles never get value candidates) | Constraint on `discover` (p1-G) |
| `tools/run_tutorials.py:127,200-221`, `tests/conftest.py`, `tests/support/cli_runner.py:67-78` | Docs runner groups; environment isolation; in-process CLI calls (p1-M, p2-S) |
| `docs/reference/*`, `docs/how-to/repair-a-missing-claim.md`, `docs/compatibility.md`, `docs/development/documentation.md` | Public docs, release-note rule, house style |

A `gnd coverage MODEL` census counts experiment claims; it says nothing about
whether a runtime diagnostic or a disclosure switch exists.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | For an empty join, report the join variables (issue) | requested | NM1: `roles` per pair |
| O2 | Report a few values from each side differing by case, whitespace or punctuation (issue) | requested | NM1 |
| O3 | Keep exact matching (issue) | requested constraint | NM-R1 |
| O4 | Tell a spelling gap from a missing fact (issue, "Why") | requested outcome | NM1; NM3 how-to section |
| O5 | Replace the host-side case-fold workaround (issue) | requested outcome | NM1-C1 |
| O6 | A general mode: no redaction behind the public interface, redaction facing customers `(o1)` | owner requirement | NM2 |
| O7 | Near-miss values redacted wherever why-not values are (WN-R5; `(o1)`) | inherited + owner | NM3 view and schema; NM2 mode |
| O9 | Bounded work, counter tests (standing rule 2) | inherited | NM1-C4, NM2-C1 |
| O10 | Totality over hostile input, including the mode setting (standing rule 1) | inherited | NM2-C1 |
| O11 | API, CLI, schema pins; RF1/RF5 goldens | cross-cutting | NM2-C5, NM3-C2 |
| O12 | Docs and release notes (`compatibility.md:7-9`) | cross-cutting | NM3-C4, NM4 |
| O13 | Downstream anonymity | owner constraint | NM-R8 |
| O14 | Reporter acceptance in their repair loop | carried | the reporter, after merge |
| O15 | A plan to update the documentation `(o2)` | owner requirement | NM4 |
| O16 | Visible checkpoints before work is complete, docs early (owner's standing preference) | owner preference | NM4 checkpoints |
| O17 | Agent-bound streams must not leave the operator's boundary unredacted; `discover` ruling of 2026-10-25 | inherited + `(p1-G)`, `(p2-R)` | NM2-C2 rows "unchanged in every mode"; NM2-C4 forwarding only `customer` |

O8 of r1 (WN2-R1 schema residual) is withdrawn: WN2 fixed it
(`003-phase-WN2.md:119`). (p1-H)

## 2. Contract proposal and product behavior

All of this is proposed unless §10 marks it ruled.

### 2.1 Near-misses (NM1, NM3)

**Where.** On every blocker of kind `atom` (positive body atom), at any descent
depth. Not on `negated`, `comparison` or `head` blockers (NM-D6).

**Normalization `N(v)`** (NM-D4, `(o1)`), defined only for `str`:

1. Unicode NFKC;
2. `str.casefold()`;
3. delete every character whose Unicode general category starts with `P`;
4. replace each maximal run of characters for which `str.isspace()` is true
   with one U+0020, then strip leading and trailing U+0020.

`N(v)` is undefined for non-`str` values (including `bool`), and a value with
`N(v) == ""` never near-matches. Consequences stated in the docs: `ACME-CORP`
near-matches `ACMECORP`, not `ACME CORP`; `Acme . Corp` near-matches
`Acme Corp`; `℅` near-matches `co`. (p1-P, p2-Z) `N` follows the running
interpreter's Unicode database. (p1-Q)

**Eligible rows** (p1-A, p2-Y). Let the blocker's atom have roles `R`,
partitioned into constant roles, bound-variable roles `B` (variables bound in
the bindings that reached the blocker) and free-variable roles. A row `f` of
the atom's fact type (the rows the join read, `_Walk.facts`) is **eligible**
when it has every role of the atom, every constant role matches by identity,
and every free variable that occurs in two or more roles has the same identity
at each of them.

This departs from production in one stated way. Production (unseeded) also
checks that a *bound* variable repeated at several roles has one identity
within the row (`extensions.py:667-670`). Eligibility drops that in-row check:
each occurrence is compared with the binding instead (exactly or by `N`), so a
row spelling the variable `w1` at one role and `W1.` at another is a candidate
for a binding `w1`. The exactness invariant still holds: a row that agrees
exactly with a binding at every occurrence also passes production's in-row
check and would have joined.

**Near-miss pair (row-level, NM-D3, `(o1)`).** For a binding `b` that reached
the blocker and an eligible row `f`, `(b, f)` is a near-miss when every role in
`B` matches exactly or `N` is defined and equal on both sides, and at least one
role in `B` differs exactly. A blocker with `B` empty has no near-misses.

**Counting without enumerating** (p1-C, p2-Y). Key each eligible row and each
binding by the tuple, over sorted `B`, of `("n", N(v))` when defined and else
`("x", identity(v))`. `near_miss_count` is the number of distinct
(`B`-projection of a binding, `B`-projection of an eligible row) pairs that
form a near-miss; projections are distinct by identity. Within one key every
such combination is a near-miss, because an exact match would have joined (the
exactness invariant), so the count is the sum over keys of the product of the
two distinct-projection counts. Each identity group is represented by its
canonical minimum (smallest `canonical` encoding), so `1` and `1.0` in
different orders give the same bytes. The reported pairs are the 5 smallest by
`(canonical(sample), canonical(candidate))`, built from at most 5 sorted
samples × 5 sorted candidates per key. Cost: one inspection for every row of
the fact type and for every binding; at most 25 pairs built per key.

**Truncation** (p1-C, p2-X). The search has its own inspection counter, capped
by a new `WhyNotLimits.near_miss_inspections` (default 200,000, checked like the
other ceilings). Bindings are inspected before rows, so a truncated search
still reports what it can. Reaching the cap stops the search and sets
`near_miss_truncated: true`; `near_miss_count` is then a lower bound and the
pairs are those found so far. The counter is not part of `work`. The request's
status and exit are unaffected. Inspections never exceed the probes the join
already charged, so at default limits the flag is always false; the docs say
so, and tests reach it with lowered caps.

**Payload (raw view).**

```json
"near_miss_count": 1,
"near_miss_truncated": false,
"near_misses": [
  {"roles": ["party"],
   "sample": {"party": "Acme Corp.", "case": "c-9"},
   "candidate": {"party": "ACME CORP.", "case": "c-9"}}
]
```

`sample` is `b` projected onto `B`, keyed by role; `candidate` is `f` projected
onto `B`; `roles` is the sorted set of roles differing exactly. The three fields
are present on every atom blocker once the search is enabled; an empty list with
count 0 means "searched, none". Redacted view: `near_miss_count` and
`near_miss_truncated` are shown; `near_misses` is `"redacted"` (NM-D17).

**Enablement** (p1-B). The kernel takes `near_misses: bool = False`. In NM1 no
public path enables it, so NM1 changes no public byte. NM3 enables it in the
service together with the schema bump.

### 2.2 Disclosure mode (NM2)

**Values (NM-D1 ruled `(o1)`; shape NM-D12 ruled `(p1-E)`).**

| Mode | Check family (declared redaction) | Witness lane (`witness`, `witness-view`, `replay`, `why-not`) and `lean`, `souffle*` outputs | Raw requests on these surfaces |
|---|---|---|---|
| unset | today | today | today |
| `internal` | not applied (as `unredacted=True`) | raw in CLI and API | allowed |
| `customer` | applied | redacted in CLI and API: `api.why_not` returns the redacted view; `api.witness` and `api.replay` return the CLI's default view; no raw certificate | refused |

`customer` therefore withholds declared-sensitive values in check-family
outputs and every population value in witness-lane, `lean` and `souffle*`
outputs. It does not redact undeclared values in check-family messages; the
docs say so and point to `redact: true` declarations. (p1-E, p2-V) The
accepted proposal named the check family and the witness lane; covering the
`lean` and `souffle*` raw options is the author's reading of "the witness lane"
(those exports' default outputs are value-free and their raw options expose
witness values), not a ruling of `(p1)`. (p2-V)

**Unchanged in every mode** (NM-D13, `(p1-G)`, `(p2-T)`). These emit what they
emit today in every mode, and `disclosure.md` lists them:

- the three session output kinds (agent feedback, attempts, results: their wire
  fixes `applied`, and feedback goes to agents that may be external providers);
- `discover` (2026-10-25 ruling);
- ILP export (keeps refusing declared roles; writes undeclared values);
- `fidelity` (quotes extracted facts);
- any further row NM2-C2 classifies *emits values in every mode*.

None of them accepts a raw option.

**Setting it (NM-D2, proposed).** Environment variable `GND_DISCLOSURE`, value
exactly `internal` or `customer`; and a root CLI option
`gnd --disclosure {internal,customer}`, accepted only before the subcommand (help
and `cli.md` say so). Resolution, in order (p1-D, p2-S):

1. On a disclosure-bearing command (one with a site or a spawner row), a
   malformed `GND_DISCLOSURE` (anything but the two values, including `Customer`,
   `customer ` and the empty string) is refused with exit 3 before the option is
   looked at, even when `--disclosure` is given. Other commands ignore it.
2. If the environment says `customer`, the option may only say `customer`;
   `--disclosure internal` is refused (exit 3).
3. Otherwise the option, if given, wins for that invocation; else the
   environment; else unset.

The CLI sets a context variable in `gnd.disclosure` and resets it in a
`finally` when `main` returns, so in-process callers (`tests/support/cli_runner.py`)
see no leak. API functions call the resolver, which reads the context variable
and the environment and returns `customer` when either says so. No per-call API
keyword.

**Projection points** (p2-U). Witness-lane projection happens in thin `gnd.api`
wrappers around `witness.service` (ending the identity aliases at
`api.py:109-118`, recorded in the milestone shim inventory) and in
`witness/cli.py` after it has read the certificate; it never happens in the
shared service functions, whose raw result `gnd witness` needs
(`witness/cli.py:68`). Check-family resolution happens in the shared
`api._run_*` helpers that both the API and the CLI handlers call
(`commands/checking.py:34`). The NM2 spec names the code.

**Refusals and bands** (p1-K). A bad or repeated `--disclosure` value is a usage
error, exit 64, through the existing `_BandSafeParser`/`_StoreOnce` path. A
malformed environment value, a raw request in `customer` and a loosening option
exit 3 with a message naming the variable or option, never a value. The exact
refusal payload per lane (check-family envelope, why-not and witness envelopes,
export, judgment error reason, API `ValueError` text) is specified in the NM2
spec; any enum addition is recorded there as a schema change.

**Child processes** (NM-D16, ruled `(p2-R)`). Only `customer` is passed on.
Under `customer`, every spawner that runs GND or an agent adds
`GND_DISCLOSURE=customer` to the child's environment: `exp run` through both
agent paths (`agents._private_environment` and the schema-v6 command policy
environment at `exp/adapter_policy.py:303-312`), the value passed as a
parameter from `gnd.exp` (NM-R7) with `EnvironmentFact` provenance `supplied`
(`process.py:31`); `gnd solve` through the environment of the stations it
starts (its recorded argv unchanged). Under `internal` or unset, every child
environment is byte-identical to `33c260e`. `verifier_environment()` never
carries the mode, so session kinds stay `applied`. Forwarding sets a default
for children, not a lock: an agent controls its own environment, and the docs
say so. The NM2 spec enumerates every spawner mechanically and gives each a
rule (forwards, or does not run GND and an agent).

**Reporting.** Outputs that report a redaction mode keep their field; why-not
keeps `view`. No new field in any check-family report.

**Customer-mode contract changes** (p2-V), for the release note: `api.witness`
and `api.replay` return the view shape instead of the raw result;
`api.why_not` returns the redacted view; check-family, witness-lane and export
raw requests exit 3 or raise; any refusal enum the NM2 spec adds.

## 3. Dependencies and artifact homes

NM1 and NM2 are independent. NM3 needs both. NM4 needs NM3; its checkpoint DC1
needs only the approved plan, DC1b needs NM2. Close follows NM4. Nothing depends
on provider review, downstream execution, publication or certification. DC1b
moved from after NM1 (r1) to after NM2 because NM1 has no public path and the
disclosure how-to needs the mode. (p2-AA)

| Artifact | Home |
|---|---|
| Plan, specs, records, reviews | `.gnd-planning/milestones/why-not-near-misses/` |
| Normalization and near-miss search | `src/gnd/witness/why_not.py` (NM1) |
| Disclosure resolver | `src/gnd/disclosure.py`, layer-map entry beside `gnd.redaction` (NM2; NM-D7) |
| CLI option | root parser in `src/gnd/cli.py` (NM2) |
| Witness-lane API wrappers | `src/gnd/api.py`, shim inventory entry (NM2) (p2-U) |
| Packaged example with a `redact: true` role | `src/gnd/examples/disclosure/` (name fixed in the NM2 spec), listed in `tools/check_installed_docs.py` (NM2) (p1-O) |
| Example population with a spelling gap | `src/gnd/examples/quoted_claims/spelling-gap.pop.json` (NM3) |
| Schema | `src/gnd/why-not.schema.json`, `gnd-why-not/2` (NM3) |
| Goldens | NM1: inline kernel fixtures in `tests/test_why_not_kernel.py`; NM3: `tests/fixtures/why_not/` regenerated (p1-P) |
| Docs | NM3: normative near-miss section and how-to section; NM4: everything else (p1-N) |

## 4. Phases

### NM1: Near-miss search in the kernel (about 120 source lines, 400 test lines)

Spec: [phase-NM1-spec.md](phase-NM1-spec.md), r3, awaiting its owner gate.

- **NM1-C1:** `N` as §2.1, one function; unit cases discriminating step order
  and deletion versus replacement.
- **NM1-C2:** eligible rows (a named helper), keyed counting over distinct
  projections, canonical-minimum representatives, the 5 reported pairs, at
  every descent depth, behind `near_misses=False`; the exactness invariant
  raised as `WhyNotInternalError`.
- **NM1-C3:** the independent oracle gains its own brute-force near-miss
  computation (own normalization, own eligibility, own representative rule);
  its random generator gains spelling variants; exact agreement on every
  untruncated case with a recorded floor of non-empty reports; a lowered-cap
  pass where every truncated kernel report has count ≤ and pairs ⊆ the
  oracle's. (p2-X)
- **NM1-C4:** the inspection counter and cap with literal truncation tests under
  lowered caps, inspections observed by bracketing the cap, a pair-construction
  count of at most 25 per key, including the n×n case that was quadratic in r1.
  (p2-Z)
- **NM1-C5:** with the flag off, every existing kernel, oracle and public test
  and golden is unchanged.

### NM2: Disclosure mode (about 350 source lines, 600 test lines; about 18 modules)

- **NM2-C1:** `gnd.disclosure` resolver and context variable; the resolution
  order and tighten-only rule of §2.2; `customer` from either source winning in
  the resolver; the token reset after each in-process `main`; refusals and
  bands; hostile values (empty, very long, non-ASCII, mixed case, trailing
  space) cased, including a malformed variable with `--disclosure internal`
  (exit 3) and `gnd check … --disclosure customer` (exit 64). (p2-S)
- **NM2-C2:** the disclosure table. Every leaf of the root parser tree (57 at
  `33c260e`) and every public callable of `gnd.api` at module level (including
  `judgments`), its classes' public methods and `gnd.export.service`, plus the
  output kinds of `redaction.emitter_specs()` and `admission`, has exactly one
  row: *site* (behaviour per mode stated), *value-free*, or *emits values in
  every mode* (listed in `disclosure.md`). A surface without a row fails the
  test, and a reverse check fails any row that does not resolve to live code.
  Rows known at `33c260e` include the 4 witness-lane views, `witness --out`,
  the 4 export raw parsers and their 4 Python functions, `judgments
  --unredacted` and `api.judgments`, `api.check_with_receipt` and the other
  `unredacted` API functions (named in the spec),
  `EvaluationSession.check/check_with_receipt/transition`, `api.witness`,
  `api.replay`, `api.why_not`, the 13 output kinds; and, as *emits values in
  every mode*, ILP export, `discover`, `fidelity` and the session kinds.
  (p1-F, p2-T)
- **NM2-C3:** a `customer` leak test per site using the packaged redaction
  example and why-not values: declared-sensitive values absent from check-family
  outputs; all population values absent from witness-lane, `lean` and
  `souffle*` outputs; every raw request and loosening option refused with the
  specified payload. `internal`: raw per site. *Emits values in every mode*
  rows: identical bytes across modes. The projection points of §2.2 are where
  the spec says, and `gnd witness` still writes its certificate under every
  mode. (p2-U)
- **NM2-C4:** spawners: the mechanical list with a rule per spawner; tests for
  both `exp run` agent paths and `solve`, each showing `customer` forwarded and
  the child environment byte-identical to `33c260e` under `internal` and unset;
  a test that `verifier_environment()` never carries the mode. (p2-R)
- **NM2-C5:** unset parity on every existing contract fixture; regenerated RF1
  goldens listed (12 cli-exit goldens with the root usage line, `cli/tree.json`,
  three `cli-help/gnd.py31{1,3,4}.json`, `tests/fixtures/rf1-pins/goldens.sha256`
  and `MANIFEST_SHA256` in `tests/test_rf1_pin_harness.py`). (p1-J, p2-AA)
- **NM2-C6:** environment isolation: an autouse fixture in `tests/conftest.py`
  and `run_pages` in `tools/run_tutorials.py` remove `GND_DISCLOSURE`; a negative
  control sets it ambiently and shows the parity gates unchanged. (p1-M)
- **NM2-C7:** the packaged redaction example; CLI help for `--disclosure`,
  stating it is a root option.

### NM3: Public surface (about 60 source lines, 250 test lines)

Approval instrument: corpus-first (goldens for both views, schema negatives,
exits), as WN2.

- **NM3-C1:** the service enables the search; `gnd why-not` and
  `gnd.api.why_not` emit the three fields in both views and honour the mode.
- **NM3-C2:** schema `gnd-why-not/2`, in the shared closed `$defs/blocker`:
  `near_miss_count` (integer ≥ 0), `near_miss_truncated` (boolean) and
  `near_misses` as `oneOf [array of pair objects, maxItems 5; const
  "redacted"]`, the three required only when `kind` is `atom` (`if`/`then`);
  per-length `if`/`then` clauses so `near_miss_count` ≥ the list length;
  `near_misses: {"const": "redacted"}` in `redacted_clause.blocker`. Negative
  cases: raw `near_misses` under `view: redacted`, a missing field on an atom
  blocker, the fields on a non-atom blocker, count below the list length, six
  pairs. Regenerated: `tests/fixtures/why_not/goldens`,
  `tests/fixtures/rf5-handlers/answers.json` (`gnd-why-not/1` → `/2`), and the
  docs outputs that print whole payloads. (p1-H, p1-P, p2-AA)
- **NM3-C3:** the spelling-gap example population and a committed repair test
  built only from payload fields, with a negative control (a candidate whose
  other bound role differs is not reported).
- **NM3-C4:** docs owned here (p1-N): the normative near-miss section of
  `docs/reference/why-not.md` (the one home of `N` and the rule, moving from the
  NM1 spec, including that the truncation flag is false at default limits); the
  section "When the values are spelled differently" in
  `docs/how-to/repair-a-missing-claim.md`; the regenerated why-not outputs in
  that page and `python-api.md`; a release-note entry with the `/2` migration
  line. Docs gates exit 0.

### NM4: Documentation

House style per `docs/development/documentation.md`; anonymity per NM-R8. No
business tutorial page is in scope; if the owner adds one, it shows skill
prompts and results, not code. Every output shown comes from a real run
(`gnd-run` blocks executed by `tools/run_tutorials.py`); nothing is fabricated.

**Checkpoints (owner-visible, before the work is complete).** (p1-O)

- **DC1, after plan approval:** drafts of `reference/disclosure.md` and the
  near-miss section of `reference/why-not.md`, rendered locally, with example
  payloads marked *illustrative*. The owner's reaction can amend NM2/NM3 specs.
  Not committed to `docs/`.
- **DC1b, after NM2:** the disclosure how-to rendered with real runs over the
  packaged redaction example.
- **DC2, after NM3:** every changed page rendered with real output, before the
  NM4 record.

**Inventory and planned change.** From
`git grep -li 'redact\|--raw\|unredacted\|why-not' 33c260e -- docs src/gnd/skills`
(28 files); the NM4 spec re-runs it and records a disposition for every hit.
(p1-O)

| Page | Change |
|---|---|
| `docs/reference/disclosure.md` (new) | The one home for the mode: three states, how to set it, the resolution order and tighten-only rule, the threat model (protected party; guard, not lock, in process; the near-miss membership signal), the disclosure table (generated from NM2-C2, not hand-listed), what customer refuses and with which exit, what emits values in every mode and why, child processes receive only `customer` and that forwarding is a default, unset = today. Nav under Reference. |
| `docs/reference/why-not.md` | Beyond NM3's normative section: how the mode applies; `/2` notes. |
| `docs/reference/cli.md` | Root `--disclosure` (root-only); line 24's paragraph and the witness/why-not rows cite `disclosure.md`; exit paragraph gains the refusal and the 64 usage case. |
| `docs/reference/python-api.md` | Lines 273-275, 336, 345-346 cite `disclosure.md`; behaviour of `unredacted=True`, `raw=True` and raw witness results under `customer`. |
| `docs/reference/capabilities.md` | Why-not row (line 21) mentions near-misses; a row for the mode. |
| `docs/reference/formats.md` | A why-not schema row in the canonical-references table. |
| `docs/reference/discover.md`, `docs/reference/ilp-bridge.md` | One sentence each: unchanged in every mode, and why. |
| `docs/how-to/disclosure-mode.md` (new) | "Run GND behind your interface or in front of customers": set the mode, one check over the packaged redaction example in both modes, a refused `--raw` in customer mode, all as `gnd-run` blocks. Nav under How-to guides. |
| `docs/guides/exports.md`, `docs/agents/export-and-review.md` | One sentence each citing `disclosure.md`. |
| `docs/runtimes/lean.md`, `souffle.md`; `docs/bookrec/*`, `docs/expense/*`; `docs/development/architecture-audit.md` | Expected unchanged (they run with the mode unset or describe history); disposition records why. |
| `docs/release-notes.md` | Disclosure-mode entry with the customer-mode contract changes of §2.2 (the near-miss entry is NM3's). |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md`, `orm-meta.schema.json` | The `redact` declaration's home: one sentence on how `customer` uses it; schema description only if it states redaction behaviour. |
| `src/gnd/skills/gnd-export/SKILL.md`, `references/export-contract.md` | Near-miss fields in the why-not route; customer refuses raw exports. Packaged-skill pins updated. |
| `src/gnd/skills/gnd-dev-session/` references; `gnd-model-evolve/references/evolution-contract.md` | Sessions unchanged in every mode (one sentence), or unchanged with a reason. |

- **NM4-C1:** the disposition table is complete and committed in the NM4 record.
- **NM4-C2:** DC1, DC1b and DC2 shown to the owner, with reactions recorded.
- **NM4-C3:** new pages registered in `tools/run_tutorials.py` `groups()` and in
  `tests/test_documentation_tutorials.py` parametrization; `tools/run_tutorials.py`,
  `zensical build --strict`, `tools/check_docs.py site`,
  `tests/test_documentation_tutorials.py`, `tests/test_plan_app_docs.py` and
  `tools/check_installed_docs.py` exit 0.
- **NM4-C4:** one-home check: `N` and the near-miss rule in `why-not.md` only;
  the mode table in `disclosure.md` only; a grep test enforces both.
- **NM4-C5:** an independent docs review (one local reader) against shipped
  behaviour.

### Milestone close (not a feature phase)

Final parity, the four-reader close review (NM-D9), the question sweep,
carryover O14 to the reporter, and a PR.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1, O2 | NM1-C2, C3 |
| O3 | NM-R1; NM1-C5 |
| O4 | NM1-C2; NM3-C3, C4 |
| O5 | NM1-C1 |
| O6 | NM2-C1..C3 |
| O7 | NM3-C1, C2; NM2-C3 |
| O9 | NM1-C4; NM2-C1 |
| O10 | NM2-C1 |
| O11 | NM2-C5; NM3-C2 |
| O12 | NM3-C4; NM4 |
| O13 | NM-R8 |
| O14 | close carryover |
| O15 | NM4-C1..C5 |
| O16 | NM4-C2 |
| O17 | NM2-C2, C3, C4 |

## 5. Documentation, skill and compatibility surfaces

- New: three why-not payload fields under `gnd-why-not/2` (NM3); one environment
  variable; one root CLI option; two pages.
- **With the mode unset:** disclosure behaviour and child environments are
  unchanged; the why-not payload changes in NM3 and root help changes in NM2,
  both released with notes; no change to `check`, `witness` or `replay`
  contracts, exit bands, or report schemas. (p1-J, p2-V)
- **Under `customer`:** the contract changes listed at the end of §2.2, in the
  release note. Under `internal`: raw results where the default is redacted, as
  if every raw option were passed.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Near-misses read as "these are the same entity" | Docs and field names say candidate; NM-R1; how-to negative control |
| Valid input crashes the search | Eligibility mirrors production's per-row checks with one stated relaxation (§2.1); repeated-variable cases; oracle with its own eligibility |
| Normalization drifts | NM-R2 one home; oracle implementation; discriminating T1 |
| Search cost or a new exit-4 path | NM-R3 keyed counting, pair-construction bound and own cap; not charged to `work` |
| A disclosure surface escapes the mode | NM2-C2 total table over parser leaves and public callables, with a reverse check |
| `customer` bypassed by the CLI option or a mistyped variable | Tighten-only; malformed variable refused first; `customer` wins in the resolver (NM-R6, §2.2) |
| `customer` read as "no values anywhere" | §2.2 states the per-convention scope and the *emits values in every mode* list; docs point to `redact: true` |
| Values leave through agents or children | Session kinds unchanged in every mode; only `customer` forwarded; verifier environment pinned |
| Redacted count leaks membership | Named in the threat model (NM-D17) |
| Ambient environment changes gates; CLI tests leak mode | NM2-C6 scrub and negative control; token reset |
| Docs describe the plan rather than the code | Pages written after code; DC1 illustrative and uncommitted; NM4-C5 |
| Docs drift into two homes | NM4-C4 |
| Downstream names leak | NM-R8 |
| A repair round introduces defects | §8 stop rule applied; r3 carries no opinion; phase diff reviews read the code |

## 7. Out of scope

- Fuzzy, edit-distance, phonetic or locale-aware matching; automatic
  reconciliation of spellings.
- Near-misses for negated atoms, comparisons and head terms (NM-D6).
- Redacting undeclared values in check-family outputs (`customer` option (b),
  not selected).
- Any disclosure change to session kinds, `discover`, ILP export or `fidelity`.
- Re-projecting retained evidence written before a mode was set.
- A configuration file; per-tenant modes; protection against code running inside
  the GND process; binding an agent's own environment.
- Publication, release, certification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, owner gate,
implementation and focused tests, an independent diff review, a refactoring
review and a record. No code before recorded spec approval. Plan and close
review: four local readers (NM-D9). Round 1 read r1; the confirmation round
read r2 and stopped under the stop rule (ratio 0.82). r3 applies its repairs
with no further plan round `(p2)`; the owner decides plan approval over r3.
Work happens on a topic branch, then a PR; merge requires the owner.

## 9. Per-phase verification story

| Phase | Expected result | Focused gate |
|---|---|---|
| NM1 | Oracle agreement; truncation counters; nothing else changes | `uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py` |
| NM2 | Total table; leak and refusal per site; spawner rules; unset parity; isolation | NM1 gate plus a new `tests/test_disclosure_mode.py`, `tests/test_public_api.py`, `tests/test_rf1_cli_pins.py`, `tests/test_rf1_pin_harness.py`, `tests/test_rf5_commands.py`, `tests/test_rf5_handler_pins.py` and the redaction, session and agent-environment tests the NM2 spec names (unresolved until that spec) |
| NM3 | Goldens; schema negatives; docs gates green | NM2 gate plus `tests/test_why_not_repair_loop.py tests/test_documentation_tutorials.py tests/test_plan_app_docs.py`, `tools/run_tutorials.py`, `zensical build --strict`, `tools/check_docs.py site` |
| NM4 | All pages dispositioned and executed; checkpoints seen | NM4-C3 commands plus the one-home grep test |

The broad suite runs on explicit owner selection.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Ruling or proposal |
|---|---|---|---|
| NM-D1 | Redaction of near-miss values | (a) follow why-not's view; (b) a general disclosure mode | **Ruled `(o1)`: (b).** |
| NM-D2 | How the mode is set | (a) env var + root CLI option (tighten-only), no API keyword; (b) also an API keyword; (c) a config file | **Ruled `(a1)`: (a)** (p1-D) |
| NM-D3 | Several bound roles | (a) row-level; (b) per role | **Ruled `(o1)`: (a)** |
| NM-D4 | Normalization | §2.1 four steps | **Ruled `(o1)`**, with the stated Unicode-database dependency (p1-Q) |
| NM-D5 | Cap and count | 5 pairs; full count | **Ruled `(o1)`**; truncation per NM-D14 |
| NM-D6 | Which blockers | (a) positive atoms only; (b) also negated atoms | **Ruled `(a1)`: (a)** |
| NM-D7 | Resolver home | (a) `gnd.disclosure` beside `gnd.redaction`; (b) inside `gnd.redaction` | **Ruled `(a1)`: (a)** |
| NM-D8 | Why-not schema version | (a) `gnd-why-not/2` (closed schema); (b) stay `/1` | **Ruled `(a1)`: (a)**, with a migration line |
| NM-D9 | Plan and close review instrument | (a) four local readers; (b) six-seat panel | **Ruled `(a1)`: (a)**, read from `(o2)`, confirmed at the plan gate (p1-I) |
| NM-D10 | Customer-mode refusal band | (a) exit 3; (b) exit 64 (usage): wrong for a valid command refused by policy; (c) a new band | **Ruled `(a1)`: (a)** for refusals; 64 stays for malformed option values (p1-K) |
| NM-D11 | Docs checkpoint DC1 before code | (a) illustrative drafts after plan approval; (b) docs only after code | **Ruled `(a1)`: (a)**, plus DC1b real runs after NM2 |
| NM-D12 | What `customer` withholds | (a) declared roles in the check family + every value in witness-lane outputs (the author reads `lean`/`souffle*` raw options as witness lane); (b) every value everywhere | **Ruled `(p1-E)`: (a)**; the `lean`/`souffle*` reading is the author's (p2-V) |
| NM-D13 | Session kinds, `discover`, ILP export | (a) unchanged in every mode; (b) follow the mode | **Ruled `(p1-G)`: (a)**; `fidelity` joins the list as found (p2-T) |
| NM-D14 | Can the search fail a request | (a) own cap, truncate with a flag; (b) charge `probes`, record exit-4 exposure | **Ruled `(p1-C)`: (a)** |
| NM-D15 | NM1 public diff | (a) search off on the public path until NM3; (b) accept changes in NM1 | **Ruled `(p1-B)`: (a)** |
| NM-D16 | What child processes receive | (a) only `customer`, child environments otherwise as today; (b) the resolved mode, `internal` included: lifts declared redaction for agents that may be external providers | **Ruled `(p2-R)`: (a)** |
| NM-D17 | Near-miss count in customer mode | (a) keep `near_miss_count` and `near_miss_truncated`, name the membership signal in the threat model; (b) a boolean only | **Ruled `(p2-W)`: (a)** |

No open question is inherited from an earlier milestone.

## Close note (2026-11-02)

Appended at milestone close. The r3 text above is left as approved; where it
and this note differ, this note states what happened.

- **Execution has occurred.** The header's "Phase execution, implementation and
  publication have not occurred" and §4 NM1's "awaiting its owner gate" are
  superseded: NM1-NM4 were specified, approved `(s1)`-`(s5)`, implemented and
  committed (records `001`-`004`), and the close is
  [005-milestone-close.md](../005-milestone-close.md). Nothing is published.
- **Refuted premises.** Each phase spec records the plan premises it found
  false (the NM2 spec's "Corrections to the plan, found at harvest", the NM3
  and NM4 specs' H-rows). They are the repair the specs deferred to this
  close; the r3 text is not edited.
- **NM-R6 "one signal".** The threat model's single named signal (the
  redacted near-miss count) understated what customer mode reveals. The
  status, the exit code and the per-step counts of `why-not`, `witness` and
  `replay` also confirm whether a caller-supplied row matches exactly (close
  reader 2, F1). `docs/reference/disclosure.md` now names both; the
  near-miss count is the one signal this milestone added.
- **NM3-Q1.** The installed-docs check takes `--out <new dir>`:
  `uv run python tools/check_installed_docs.py --out <new dir>`. The NM3
  spec's Verification-selection row omitted it.
- **`DisclosureRefused` in `gnd.api.__all__`.** Added in NM3 (DC1b finding);
  two exact-inventory pins outside the NM3 gate (`tests/test_v61_phase2_api.py`,
  `tests/test_public_runtime.py`, a distribution-lane test) were updated at
  close.
