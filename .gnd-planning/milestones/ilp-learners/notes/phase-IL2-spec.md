# IL2 — ILASP / FastLAS adapter

## 1. Status

**Draft r1, 2026-10-27. Awaiting this phase's owner gate.** `auto=false`.
- **Nothing exists yet.** Nothing is implemented, downloaded, installed or
  run.
- **Gate decisions:**
  - **IL2-D1:** the learner, with its licence (IL-R5). This decision
    stops for the owner's ruling, because ILASP's terms are not an OSI
    licence (§7).
  - **IL2-D2:** the download.
  - **IL2-D3 and IL2-D4:** the timeout and the output-format probe.

## 2. Provenance

- **Plan:** [ilp-learners-plan.md](ilp-learners-plan.md) r3 (SHA-256
  `329449d8…6281`, owner-approved 2026-10-27 in
  [`001-plan-gate.md`](../001-plan-gate.md)). The sections used:
  - §0;
  - §1 completion predicate 2;
  - §2 "ILASP / FastLAS (IL2)";
  - §3;
  - §4 IL2;
  - §5;
  - §9's IL2 row;
  - §10.
- **Prior phase:** [`002-phase-IL1.md`](../002-phase-IL1.md), merged in PR
  #56 at `65fd6df`. IL2 uses its boundary, its open questions IL1-Q2 and
  IL1-Q3 (both targeted at IL2), and its refuted premises 3 and 4.
- **Source inspected at `65fd6df`:**
  - `src/gnd/export/ilp_learners.py`: `Learner`, `LEARNERS`,
    `EXPORT_TARGETS`, `IMPORT_TARGETS`;
  - `src/gnd/export/ilp_popper.py`:
    - `quote`, `_term`, `thresholds`, `_threshold_rows`, `render`;
    - `_comparison`, `_unparsable`, `extract_program`, `parse_program`;
  - `src/gnd/export/ilp_rewrite.py`: checks 1–10 and 9b;
  - `src/gnd/export/ilp_service.py`: `_prepare` and `_read_clauses`;
  - `src/gnd/ilp-clauses.schema.json`: the literal kinds `atom`, `compare`,
    `not`, `or` and `aggregate`;
  - the `target` enums in `src/gnd/ilp.schema.json` and
    `src/gnd/ilp-import.schema.json`;
  - `src/gnd/commands/export.py:108` and `src/gnd/commands/checking.py:452`;
  - the eight RF1 goldens that pin `{popper,neutral}` (§6, "CLI").
- **The IK6 refunds export, observed:**
  - 3 predicates (`f_refund_amount`, `f_refund_by` and `f_refund_channel`,
    each `(ex, t_refund, …)`);
  - 4 comparisons over `t_amount`;
  - 60 facts and 8 examples, each with a `label` of `pos` or `neg`.
- **Upstream facts, read-only, 2026-10-27:** these came from the GitHub API
  and the ILASP manual at `doc.ilasp.com`. Nothing was downloaded beyond
  metadata and documentation pages, and nothing was installed (§12).
- **Local probe (no learner):** clingo 5.8.2 from the IL1 scratch venv (approved
  under IL1-D3) ground the proposed comparison background on a three-line
  example and derived the expected `gt(600,500)` and `wrong` (§6,
  "Comparisons").

## 3. Obligations — inline harvest

| Obligation | Source | Discharged in |
|---|---|---|
| `--target ilasp` (and `fastlas` if IL2-D1 keeps it) renders an ASP learning task from the neutral form; golden across two `PYTHONHASHSEED` values | plan completion 2; §2; IL2-C1 | §6 export; T1 |
| The golden pins: background holds comparison definitions only, one context per example without the example argument, `#modeb` arity = predicate arity − 1 | IL2-C1; §2 | §6 export; T1, T1b |
| Learned ASP rules parse into the clause form; `wrong :- body.` becomes `wrong(X) :- body'`, the exact inverse of the rendering | completion 2; §2 | §6 reader; T3 |
| Refused by construct name: constraints, choice rules, weak constraints, classical negation, arithmetic terms, intervals and pools, directives — one test each | IL2-C2; §2 | §6 reader table; T4 |
| `not`, aggregates and disjunction reach the fragment checker and are refused by its names | §2 | §6 reader; T4b |
| The constants table: one test per kind | IL2-C2; §2 | §6 constants; T5 |
| The run-record binding and the coverage re-check reuse IK5's code, with `method: ilp-ilasp` | IL2-C3 | registry entry; T7 |
| One live run under IL-R9, licence recorded first (IL-R5), and a replay test | IL2-C4; completion 2 | §6 live run; §12; T9 |
| Adding a target moves the RF1 CLI goldens and widens both `target` enums within `/1` (D9 (o)) | plan §5; IL-R7 | §6 CLI; T2, T11 |
| A section in `ilp-bridge.md` | plan §5 | §6 docs; T12 |
| Plan §9 gate controls: RF1 pins, RF5, layering, arch, RF6, built inventory, schema inventory | plan §9 | §8 gate command |
| IL1-Q2: should the service refuse a non-exporting entry, and should `contract` vary? | IL1 record | IL2-D7 |
| IL1-Q3: should the Popper threshold parser refuse names the renderer never writes? | IL1 record | IL2-D8 |
| IL1 refuted premise 4: a rule-defined comparison is unsafe for a learner that grounds the background | IL1 record | §6 "Comparisons": ground `thr_` facts plus domain-bound rules; the T-live check |
| Skill pin sites naming `gnd export ilp`: inspected, edited only if behaviour changed | plan §5 | §6 docs (no edit: `gnd-export/SKILL.md:36–38` names the command, not its targets) |
| IL-R1 to IL-R11 and IK-R1 to IK-R12 | plan §0 | §4 |
| D3 (a) (o): no GND command runs a learner | plan gate | unchanged |
| D10 (o), IL-R11: all-or-nothing admission | plan §10 | unchanged; any refusal refuses the import |

## 4. Rules bound to IL2 (every plan §0 rule by name)

**Standing rules.**

| Rule | Binding |
|---|---|
| 1 Totality | **New loader:** the ASP hypothesis reader, `ilp_asp.parse_hypothesis`.<br>**Caps:** 1 MiB of text (`CLAUSES_CAP`), 32 rules, 16 body literals, nesting depth 4 and 32 integer digits, each capped before it is read.<br>**Refusals:** every input outside the grammar exits 3 `unparsable` with line and column; every construct in the §6 refusal table exits 3 with its name; no traceback (T6).<br>**A second new reader:** the hypothesis extractor `ilp_asp.extract_hypothesis`, shared by the script and T9. |
| 2 Algorithm bound | **The reader** is linear in tokens. **The renderer** is linear in facts plus thresholds, with at most 32 thresholds per integer type (`ilp_popper.thresholds`, reused). **The import's** work counter is unchanged. |
| 3 Validation order | The reader's refusals come before the fragment checker. Checks 1–10 and 9b keep their order and names. A construct the clause form can carry (`not`, aggregate) is passed through so that the checker names it. |
| 4 One walk | **One registry entry.** **One fragment checker** (`ilp_rewrite`). **One threshold selection** (`ilp_popper.thresholds`). **One run binding and coverage re-check** (`ilp_service`). The ASP module adds a renderer and a reader only. |
| 5 One home | `docs/reference/ilp-bridge.md` gains one ILASP section: the rendering, the reader's fragment table, the constants table and the refusal names. |
| 6 Measurement | **IL2-C1** is decided by golden bytes under two hash seeds. **IL2-C4** is decided by a replay test over committed bytes (T9). |

**Plan rules (IL-R).**

| Rule | Binding |
|---|---|
| IL-R1 | No ILASP, FastLAS or clingo dependency. IL1's T7 already names `ilasp`, `fastlas` and `clingo`; it stays green. |
| IL-R2 | **The script** is `evidence/IL2/run_ilasp.py`, under `run_bounded_process`. **The live check** is T-live in `tests/test_ilp_asp.py`, marked `live`. **Installs:** a scratch prefix, and only the IL2-D2 download. |
| IL-R3 | The ASP reader feeds `ilp_rewrite`, with no copy of any check. The `type-confused-join` check (9b) applies to `ilasp` (T8). |
| IL-R4 | The run record's coverage comes from clingo evaluating `background + context + hypothesis` per example, labelled "independent evaluation (clingo)". ILASP's printed figures are kept verbatim. The script never calls GND to compute coverage. |
| IL-R5 | Licences are recorded from upstream in §12 before any download. ILASP's terms are not an OSI licence, so they stop for the owner's ruling (IL2-D1). |
| IL-R6 | ILASP's stdout is untrusted. Only the extracted block reaches the capped reader. |
| IL-R7 | No wire version changes. The `target` enums of `ilp.schema.json` and `ilp-import.schema.json` widen within `/1` to add `ilasp` (D9 (o)); IL1's T2 equality test pins them to the registry. Every IK5 and IK6 golden and every Popper rendering stays byte-identical. Only the CLI help and exit goldens that list the choices move (§6, "CLI"). |
| IL-R8 | The live input is the IK6 refunds example only, with E recorded. The output-format probe (IL2-D4) reads only a toy task written in this spec. |
| IL-R9 | §6 "Live run" fixes the two outcome fields, the extractor, the settings and argv, all six `ProcessLimits`, the fixed import arguments and the amendment path. The learner's own timeout is IL2-D3. |
| IL-R10 | The script substitutes `<scratch>`, `<repo>`, `<home>` and `<user>` itself, as `run_popper.py` does. IL1's T8 scan covers `evidence/IL2/`. |
| IL-R11 | Any reader or checker refusal refuses the whole import. |

**Inherited rules (IK-R).**

| Rule | Binding |
|---|---|
| IK-R1 | Admission is unchanged: `induced`/`proposed`/`deontic` through the existing proposal builder. IL2 adds a reader, and no admission path. |
| IK-R2 | GND computes coverage and support. The run record's sets are compared, and never written into provenance. |
| IK-R3 | Every IK5, IK6 and IL1 golden is byte-identical, except the 8 listed RF1 CLI goldens (§6, "CLI") and IL1's T2 expected tuples. |
| IK-R4 | No ORM schema change. |
| IK-R5 | No new rendered free text. Host strings reach `task.las` only as ASP quoted strings, escaped (§6, "Constants"). |
| IK-R6 | No new population reads. The renderer reads the in-memory neutral form. |
| IK-R7 | `gnd.export.ilp_asp` is assigned to the `export` lane in `tools/gnd_layers.json` before use. There is no new command edge (literal `choices=`), and the allowance count stays 0. New RF6 query sites go into an IL2 successor delta chained after IL1's. |
| IK-R8 | ILASP runs only from the evidence script, bounded. |
| IK-R9 | This table and the standing-rules table. |
| IK-R10 | IL1's T8 privacy scan. |
| IK-R11 | Provenance comes from the unchanged import and carries opaque ids. |
| IK-R12 | The bias settings, limits, argv and import arguments are fixed here, before any run. |

## 5. Goal

**Export.**
- `gnd export ilp --target ilasp` writes `neutral.json`, `export.json` and
  `ilasp/task.las`. The task is byte-identical under `PYTHONHASHSEED=0` and
  `1`.
- `gnd export ilp --target {popper,neutral}` is byte-identical to `65fd6df` on
  every fixture.

**Import.** `gnd import ilp-rules --target ilasp` reads an ILASP hypothesis,
maps it to the clause form, and re-checks it through the shared checker. It
either admits the hypothesis or refuses by name.

**Live run.** One real ILASP run over the IK6 refunds export records one
`termination` value and one `import` value. A default-gate test replays its
committed bytes.

## 6. Design

### Registry entry

Appended after `neutral` (plan §2, declaration order):

```python
Learner(target="ilasp", learner="ilasp", method="ilp-ilasp", exports=True,
        render=ilp_asp.render, parse=ilp_asp.parse_hypothesis,
        contract="labelled-clauses", adapter_version=ilp_asp.ADAPTER_VERSION)  # "1"
```

As a result, `EXPORT_TARGETS == IMPORT_TARGETS == ("popper", "neutral",
"ilasp")`.

**If IL2-D1 also keeps FastLAS,** a second entry `fastlas` follows. It has the
same renderer and reader, `learner="fastlas"` and `method="ilp-fastlas"`.
The rendering differences FastLAS needs are listed under IL2-D1.

### Export: `ilasp/task.las` (`src/gnd/export/ilp_asp.py`, new)

**Line order:**
1. background;
2. constants;
3. mode bias;
4. examples.

Every section is sorted deterministically, with no set or dict iteration
order reaching the bytes.

**1. Background: the comparison definitions only (plan §2).** For each
integer type `t` that has at least one exported `gt` or `lt` comparison and
at least one observed value:

```
dom_t(V) :- p(_, …, V, …, _).        % one rule per (predicate, argument position) of type t, the example argument dropped
thr_t(c).                            % one fact per threshold c in ilp_popper.thresholds(observed values of t)
gt_t(X, C) :- dom_t(X), thr_t(C), X > C.
lt_t(X, C) :- dom_t(X), thr_t(C), X < C.
```

- **Names:** `t` is the neutral type name (for example `t_amount`), so the
  rule is `dom_t_amount`. `gt_t` and `lt_t` are the neutral form's
  comparison names (`gt_t_amount`).
- **Which comparisons:** only `gt` and `lt`, the operators IL1-A1-D2 (o)
  chose for Popper. A type without that comparison gets no rule.

**Why this shape (IL1 refuted premise 4).**
- **Grounding:** a learner that grounds the background needs every variable
  bound. `dom_t` binds `X` from the context's own facts, and `thr_t` binds
  `C` from ground facts.
- **Checked:** the IL1 scratch clingo ground exactly this shape (§2).

**`dom_t` is per context.** It holds the values of type `t` in the example's
own facts, so a comparison holds only on values the example has. This is
GND's semantics too: the comparison's variable is bound by an antecedent atom
(check 8).

**2. Constants.** `#constant(t, c).` for each threshold `c` of each type
above, ascending.

**3. Mode bias.**

```
#modeh(wrong).
#modeb(2, p(var(t1), …, var(tn))).     % per exported predicate, its types minus the example argument
#modeb(1, gt_t(var(t), const(t))).     % per rendered comparison
#modeb(1, lt_t(var(t), const(t))).
#maxv(4).
```

- **Recall:** 2 per predicate and 1 per comparison. The comparison's 1
  matches check 5, at most one comparison.
- **`#maxv(4)`:** IL2-D5.
- **`#max_penalty`:** ILASP's default of 15 applies. It is not rendered,
  and the argv is recorded.
- **No `not`, `#modeh` variants or choice heads** are offered. Anything the
  learner returns outside this bias is refused (§6, "Reader").

**4. Examples: one context-dependent example per population.**

```
#pos(e<i>, {wrong}, {}, { <facts> }).   % label pos
#neg(e<i>, {wrong}, {}, { <facts> }).   % label neg
```

- **Ids:** `e<i>` is the example's 1-based position in `neutral.examples`
  (IL2-D9). The id mapping is not written, because it is the neutral form's
  order.
- **Context:** the context holds that example's facts with the example
  argument dropped: `f_refund_amount(101,40).` One fact per line, grouped by
  predicate name (sorted). Within a predicate, the facts keep the neutral
  form's order, the same stable sort that `ilp_popper.render` uses.

**Constants (rendering and reading are inverse).**

| Neutral value | Rendered as | Read back as |
|---|---|---|
| integer `n` (including negatives) | `n` (`-3`) | integer |
| string `s` | ASP quoted string: `"` + `s` with `\` → `\\`, `"` → `\"`, newline → `\n` + `"` | string `s` |
| boolean | `true` / `false` (bare) | boolean |
| — | bare symbolic constant other than `true`/`false` (for example `web`) | string `web` (the learner can write one; the renderer never does) |

**Booleans differ from Popper.** The Popper reader reads a bare `true` as the
string `"true"` (`_Parser.term`, kind `name`), although the Popper renderer
writes a boolean as `true`. So the Popper adapter is not an exact inverse for
booleans. This is latent: no Popper bias offers a constant in a predicate
argument. IL2 does not change the Popper reader. The difference is proposed
as open question IL2-Q1 (§7). The ASP reader is the exact inverse, so it
reads a bare `true`/`false` as a boolean.

**Refused at render:** a string with a control character other than newline
exits 3 with the export's existing `unrepresentable` refusal, with a detail
naming the ASP string. The Popper renderer escapes control characters as
`\xHH\`, but an ASP string has no general escape for them. The record lists
this as a rendering limit.

**The export index.** `export.json` lists `ilasp/task.las` with its SHA-256 and
`adapter_version: "1"`, as for Popper.

### Reader: `parse_hypothesis(text) -> gnd-ilp-clauses/1` (closed, capped, total)

**Grammar.**
- **Input:** a sequence of rules `head :- body.` or facts `head.`, with `%`
  line comments ignored.
- **Tokens:**
  - identifiers, variables, integers and quoted strings;
  - `:-`, `,`, `.`, `(`, `)`, `not`;
  - the comparison operators `< <= = != >= >`;
  - every token that is refused (table below).

**Mapping (the exact inverse of the rendering).**
1. **The head** must be the atom `wrong` with no arguments. It becomes
   `wrong(X)`, where `X` is the first of `X`, `X0`, `X1`, … that the rule
   does not use.
2. **Body atoms:** a body atom whose predicate matches the comparison-name
   pattern `^(gt|lt|ge|le)_t_[A-Za-z0-9_]+$` is copied as is (`gt_t_amount(V2,
   500)`); this is the clause form IL1's `_comparison` produces. Every other
   body atom gets `X` prepended as its first argument.
3. **Handed to the checker unchanged:**
   - unknown predicates and wrong arities (check 3 names them);
   - `X`-free bodies (check 4);
   - type confusion (9b).
4. **Variables** keep the learner's names.

**Refused by the reader, each by name, with exit 3** (plan §2, plus three that
the clause form cannot carry):

| Construct | Example | Refusal |
|---|---|---|
| constraint | `:- f(V1,V2).` | `asp-constraint` |
| choice rule | `0 { wrong } 1 :- f(V1,V2).` | `choice-rule` |
| weak constraint | `:~ f(V1,V2). [1@1]` | `weak-constraint` |
| classical negation | `-f(V1,V2)` (head or body) | `classical-negation` |
| arithmetic term | `f(V1, V2+1)` | `arithmetic-term` |
| interval or pool | `f(1..3, V)`, `f(1;2, V)` | `interval-or-pool` |
| directive | `#show wrong/0.`, `#const k=1.` | `directive` |
| (p) infix built-in comparison | `V2 > 500` | `builtin-comparison` (IL2-D6) |
| (p) a fact or empty body | `wrong.` | `empty-body` |
| (p) head disjunction | `wrong \| f(V1,V2) :- …`, `wrong ; …` | `disjunction` (the checker's own name) |
| (p) a head other than bare `wrong` | `wrong(V1) :- …`, `p :- …` | `head-shape` (the checker's own name) |

`(p)` marks a row this spec proposes beyond the plan's list.

**Handed to the fragment checker** (the clause form represents them):
- `not a` becomes `{"not": a}`, which check 2 refuses as
  `negation-as-failure`;
- a body aggregate `#count{…} op k` becomes `{"aggregate": …}`, which check 2
  refuses as `aggregate`.

The `#` of an aggregate is the one `#` the reader accepts in a body.

**Extraction:** `extract_hypothesis(stdout: str) -> str`, shared by the script
and T9.
- **The proposed rule:** the hypothesis is the maximal run of lines matching
  `^wrong\b.*\.\s*$` that comes before the first line starting with `%%`.
- **Returns `""`** when no such line exists, or when stdout contains
  `UNSATISFIABLE`.
- **Confirmed or corrected by the format probe** (IL2-D4), before the run of
  record. Any correction is written into this spec before invocation 1.

### CLI, enums and goldens

- `commands/export.py:108` and `commands/checking.py:452` get `choices=("popper",
  "neutral", "ilasp")`. The help text adds ILASP: `ilasp (neutral form plus
  ilasp/task.las)`.
- **The two schema enums** add `ilasp`.
- **Goldens that move (IK-R3 exception, listed in the record):**
  - `tests/fixtures/rf1-pins/goldens/cli-help/gnd_export_ilp.json`;
  - `tests/fixtures/rf1-pins/goldens/cli-exit/gnd_export_ilp.json`;
  - `tests/fixtures/rf1-pins/goldens/cli-help/gnd_import_ilp-rules.py{311,313,314}.json`;
  - `tests/fixtures/rf1-pins/goldens/cli-exit/gnd_import_ilp-rules.py{311,313,314}.json`.

  These are regenerated through the existing RF1 regeneration path, and the
  diff is confined to the choices and help lines.
- IL1's T2 expected tuples become `("popper", "neutral", "ilasp")`.
- **No `gnd_entrypoints.json` change.**

### IL1 carry-overs

- **IL1-Q2 (IL2-D7).** IL2 adds an exporting, `labelled-clauses` entry, so
  neither question arises yet. The first non-exporting entry is `llm` (IL5),
  and the first other `contract` is `amie` (IL4). Proposed: re-target the two
  halves to IL5 and IL4, with this phase stating why.
- **IL1-Q3 (IL2-D8).** Proposed: a parser-only Popper change in IL2.
  `_comparison` refuses a threshold name the renderer never writes: a leading
  zero (`__0500`), `m0`, or `m` with a leading zero. The refusal is
  `unparsable` with line and column.
  - **No golden moves.** The renderer never writes these names, which is
    IL-R9's parser-only path.
  - **Values outside the export's threshold set** stay accepted. GND
    re-computes coverage with its own comparison over the population, so such
    a value cannot change admission. This goes in the IL2 boundary.

### Docs

`docs/reference/ilp-bridge.md` gains an "ILASP adapter" section:
- the `task.las` layout;
- the reader's mapping;
- the refusal table and the constants table.

Nothing else changes. `cli.md`, `capabilities.md` and the release notes are
IL6's (plan IL6-C2).

### Live run (`evidence/IL2/run_ilasp.py`, evidence only)

**Fixed before the run (IL-R9, IK-R12).**

| Item | Value |
|---|---|
| Input | `src/gnd/examples/refunds/model.orm.yaml` + `labels.json`, exported `--target ilasp`; E recorded |
| Learner | the IL2-D1 binary at `<scratch>/ilasp/ILASP` |
| argv | `ILASP --version=4 task.las`, run from the export's `ilasp/` directory. The flag's spelling is confirmed by `ILASP --help` at the probe (IL2-D4); any change is written here before invocation 1 |
| Settings | the rendered bias unchanged: `#maxv(4)`, recalls 2 and 1, default `#max_penalty` 15 |
| Learner timeout | IL2-D3 |
| `ProcessLimits` | `timeout_seconds` 600, `terminate_grace_seconds` 10, `stdin_limit_bytes` 0, `stdout_limit_bytes` 16 MiB, `stderr_limit_bytes` 4 MiB, `total_output_limit_bytes` 20 MiB (as IL1) |
| Environment | explicit `env`: `PATH` limited to `<scratch>/ilasp` and `/usr/bin:/bin`, plus `HOME`, `USER`, `TMPDIR` and `LANG` under the scratch prefix; the script also substitutes the placeholders itself (IL-R10) |
| Extraction | `ilp_asp.extract_hypothesis`, as above |
| Coverage | clingo 5.8.2 from the IL1 scratch venv (`python -m clingo`), per example: the background + that example's context + the hypothesis; covered iff `wrong` is in the answer set; "independent evaluation (clingo)" |
| Import arguments | `import ilp-rules model.orm.yaml hypothesis.las --labels labels.json --reported-coverage run.json --target ilasp --out proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format json`, from a fixed working directory with relative paths |

**The outcome: two fields** (closed lists, from IL-R9).

| Field | Value | Condition |
|---|---|---|
| `termination` | `rendering-rejected` | ILASP exits non-zero, citing the task |
| | `completed` | ILASP exits 0 |
| | `learner-timeout` | ILASP reports its own timeout (reachable only under IL2-D3 (b)) |
| | `wall-clock-kill` | `run_bounded_process` terminates it at the timeout |
| | `output-limit` | `run_bounded_process` terminates it at an output limit |
| `import` | `none` | `extract_hypothesis` returns `""` |
| | `refused:<name>` | `gnd import ilp-rules` exits 3, with the reader's or the checker's name |
| | `admitted` | `gnd import ilp-rules` exits 0 |

**Retained** in `evidence/IL2/live/invocation-N/`:
- `raw-stdout.txt` and `raw-stderr.txt`, sanitized;
- `hypothesis.las`;
- `run.json`;
- the import result: `import-report.json` and `proposal.json` on exit 0, or
  `import-stderr.txt` on exit 3;
- `outcome.json`, with:
  - both fields, E and `adapter_version`;
  - the versions, the licence ruling, the argv, the limits and the import
    arguments;
  - the provenance of each number;
  - "single run, reproducibility not measured".

**Invocations and fixes.**
- **Run of record:** invocation 1.
- **Another run** needs an owner ruling.
- **A rendering or settings fix** is an owner-recorded amendment that names
  the moved goldens and bumps `ilp_asp.ADAPTER_VERSION`.
- **A reader-only fix** that moves no golden stays in IL2.

**The record answers three questions:**
1. Does ILASP accept the rendering?
2. Does the hypothesis parse and import, or which named refusal does it hit?
   The refusal rate is a result, not a defect (plan §2).
3. Does clingo's coverage agree with GND's?

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IL2-D1 | Which learner, under which terms | **(a) ILASP 4.4.1 only** (target `ilasp`). A native macOS arm64 binary exists. Its terms: "free to use for non-commercial research and education"; commercial use needs a licence from its author. **This is not an OSI licence, so it stops under IL-R5:** the owner must rule whether this use qualifies. **(b) FastLAS 2.2.0 only** (target `fastlas`). MIT, with upstream digests published. Ubuntu binaries only (x86-64, and one unlabelled build), so it runs in the already-running podman Linux VM from an Ubuntu image pinned by digest, under x86-64 emulation if needed, or is built from source in the container (Boost, bison ≥ 3.6.3, flex, cmake via the container's apt). It needs a `clingo` executable in the container. Rendering differences: FastLAS needs `#bias` penalty lines and may not accept `#neg`; both are recorded at its probe. This moves the plan's `--target ilasp` (completion 2) to `fastlas`, which is a plan repair at close. **(c) Both,** ILASP as the run of record, which costs both | **(a), if the owner rules that this use is non-commercial research; otherwise (b)** |
| IL2-D2 | The download (IL-R2) | **(a):** `https://github.com/ilaspltd/ILASP-releases/releases/download/v4.4.1/ILASP-4.4.1-macOS-M1.tar.gz`, 1,982,845 bytes. **No upstream digest is published** (the GitHub asset digest is null), so the SHA-256 is computed at download, recorded in `evidence/IL2/`, and the size is checked against the figure here. The archive's member list is recorded before extraction into `<scratch>/ilasp/`. **(b):** `FastLAS_v2.2.0-ubuntu-x86-64.tar.gz`, 570,153 bytes, SHA-256 `82c10c2c…915e` (GitHub digest), plus an Ubuntu image pinned by digest at the gate | per D1; the digest is recorded at download |
| IL2-D3 | The learner's own timeout (IL-R9 asks for one below the wall clock) | ILASP documents no timeout option in its manual. **(a)** The wall clock alone (600 s), so `learner-timeout` is unreachable. This is a recorded deviation from IL-R9's clause. **(b)** If `ILASP --help` at the probe lists a timeout option, use 540 s, as IL1 did | (b) if it exists, else (a) |
| IL2-D4 | The output-format probe | Before invocation 1, run the downloaded ILASP once on a toy task fixed here: two contexts, `#modeh(wrong). #modeb(1, p(var(t))).`, with `#pos(a, {wrong}, {}, {p(1).}).` and `#neg(b, {wrong}, {}, {q(1).}).` It records `ILASP --help`, the version line and the output layout, and confirms or corrects `extract_hypothesis` and the argv. It reads no GND export (IL-R8) and is not the run of record; it is retained as `evidence/IL2/probe/` | probe |
| IL2-D5 | Bias bounds | `#maxv(4)`, recall 2 per predicate and 1 per comparison, default `#max_penalty`. **Cost:** a larger bound may let ILASP find nothing within 600 s; a smaller one may exclude a two-predicate join rule. The refunds rule Popper found needs 2 variables | as stated |
| IL2-D6 | Infix built-in comparisons in a learned rule | **(a) Refuse `builtin-comparison` in the reader.** The bias never offers them, and accepting them would reopen IL1-Q1's infix gap for a new target. **(b) Map to the clause form's `compare` literal,** which inherits IL1-Q1 | (a) |
| IL2-D7 | IL1-Q2 | Re-target: non-exporting refusal → IL5, `contract` variation → IL4 | re-target |
| IL2-D8 | IL1-Q3 | Parser-only refusal of non-canonical threshold names in IL2; out-of-set values are left to GND's re-check, and that goes in the boundary | fix in IL2 |
| IL2-D9 | Example ids in `task.las` | **(a)** `e<i>`, positional: always a valid ASP identifier, and the order is the neutral form's. **(b)** The neutral ids, quoted: readable, but ILASP's acceptance of quoted ids is unverified | (a) |
| IL2-D10 | Base and branch | `claude/il2` from `main` at `65fd6df` (the IL1 merge) | as stated |
| IL2-Q1 (proposed open question) | The Popper reader reads a bare `true` as the string `"true"`, while the Popper renderer writes a boolean as `true` | Latent: no Popper bias offers a predicate constant. Fixing it would be a parser-only change, but it would change how existing Popper output reads | carry to ilp-learners close |
| IL2-D11 | Approval instrument | **Corpus-first** for the reader: the T4 and T5 cases and the T3 hypothesis, with expected exits and clause JSON, written before the code (a serialized format, review-convergence default). **Prose** for the rendering, with the generated `task.las` golden shown in the record | as stated |

## 8. Tests

New file: `tests/test_ilp_asp.py`. Corpus: `tests/fixtures/ilp_learners/il2/`.

| ID | File | Case | Expected |
|---|---|---|---|
| T1 | `test_ilp_asp.py` | `gnd export ilp --target ilasp` over the refunds example and the IK5 corpus X1 model, in a subprocess under `PYTHONHASHSEED=0` and `1` | `task.las` and `export.json` equal the committed goldens under `il2/expected/`; both seeds byte-identical |
| T1b | same | golden structure: the background lines are only `dom_`, `thr_`, `gt_` and `lt_` rules and facts; no context fact has the example argument; every `#modeb` arity is the predicate's arity − 1; thresholds equal `ilp_popper.thresholds` | pass |
| T2 | `test_ilp_learners.py` (existing) | registry, choices and the two enums equal `("popper", "neutral", "ilasp")` | pass |
| T3 | `test_ilp_asp.py` | the corpus hypothesis `wrong :- f_refund_amount(V1,V2), gt_t_amount(V2,500).` | the committed clause JSON (`wrong(X)`, `f_refund_amount(X,V1,V2)`, `gt_t_amount(V2,500)`); `gnd import ilp-rules --target ilasp` with a matching run record exits 0 |
| T3b | same | round trip: for every fact in the refunds export, rendering the context fact and reading it back as a body atom gives the neutral values | pass |
| T4 | same (corpus `il2/refusals.json`) | one case per row of the reader's refusal table | exit 3 with that name, nothing written |
| T4b | same | `wrong :- f_refund_amount(V1,V2), not f_refund_by(V1,V3).`; `wrong :- #count{V1: f_refund_amount(V1,V2)} > 2.` | exit 3 `negation-as-failure`; exit 3 `aggregate` (the checker's names) |
| T5 | same (corpus `il2/constants.json`) | one case each: integer, negative integer, quoted string with `\"`, `\\` and `\n`, a bare symbolic constant, `true`/`false` | the constants table's readings |
| T5b | same | a string value with a control character other than newline in the export | exit 3 `unrepresentable`, nothing written |
| T6 | same | totality: unterminated string, an unknown escape, unbalanced parentheses, input over 1 MiB, 33 rules, 17 body literals, nesting depth 5, a 33-digit integer | exit 3 `unparsable` with line and column (or the cap's name), never a traceback |
| T7 | same | a run record with `learner.name` `popper` under `--target ilasp`; a run record whose coverage disagrees with GND's | exit 3 `learner-mismatch`; exit 3 `coverage-mismatch` |
| T8 | same | an `ilasp` hypothesis joining a refund id with an amount through one variable | exit 3 `type-confused-join` |
| T9 | same (default gate) | replay of `evidence/IL2/live/invocation-N/`: recompute E; `extract_hypothesis(raw-stdout.txt)` equals `hypothesis.las` (or `""`); re-run the import with the recorded arguments and assert the exit, the normalized report digest and the proposal digest, or the refusal line | pass |
| T10 | `test_ilp_learners.py` (Popper, IL2-D8) | `gt_t_amount__0500`, `gt_t_amount__m0`, `gt_t_amount__m05` | exit 3 `unparsable` with line and column; T9 of IL1 still replays invocations 1–3 |
| T11 | `test_rf1_cli_pins.py` (existing) | the 8 moved goldens, regenerated with `GND_RF1_CAPTURE` | pass without the capture variable; `git diff --stat` touches only those 8 files |
| T12 | `test_ilp_asp.py` | the `ilp-bridge.md` ILASP section | lists every refusal name and constants row from the reader's own tables, and nothing else; fails if the code or the doc drifts |
| T-live | `test_ilp_asp.py`, `live` | clingo over the rendered refunds task's background + every context + the T3 hypothesis gives the same covered set as GND's import of T3 | pass (scratch clingo) |

**Gate command (literal):**

```
uv run pytest -q -p no:randomly tests/test_ilp_asp.py tests/test_ilp_bridge.py tests/test_ilp_learners.py tests/test_ik6_walk.py tests/test_ik_close.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_public_built_inventory.py tests/test_schema_sync.py
```

The expected exit is 0. The live lane runs separately with the scratch
clingo. `slow_cadence` (`uv run pytest -q`) stays an explicit owner selection.

## 9. Out of scope for this phase

- every adapter other than `ilasp` (and `fastlas`, if IL2-D1 keeps it);
- IL1-Q1, the infix comparison in 9b (IL4);
- learning `not`, choice rules, constraints or weak constraints. The reader
  refuses them, and admitting them is out of scope for the milestone (plan
  §7);
- a GND command that runs a learner (D3 (a));
- `cli.md`, `capabilities.md`, the release notes and the comparison table
  (IL6);
- any wire version change.

## 10. Size

Estimate:
- ~260 source lines: the renderer, reader, extractor and registry entry, the
  Popper canonical-name check, and the CLI tuples;
- ~380 test lines, plus the corpus;
- one evidence script of ~220 lines;
- docs, ~60 lines.

## 11. Approval instrument

IL2-D11:
- **Corpus-first for the reader.** The T3, T4 and T5 corpus files, with their
  expected exits and clause JSON, are committed before the reader exists, and
  the harness lands red.
- **Prose for the rendering.**
- **No review panel** over the spec bytes is proposed. The process-phase
  default omits a phase-spec panel.

## 12. Licences and downloads (IL-R5, recorded 2026-10-27, before any download)

| Component | Licence or terms | Source |
|---|---|---|
| ILASP 4.4.1 | **Not an OSI licence.** The upstream README and release notes say ILASP is "free to use for non-commercial research and education"; commercial use needs contact with the author. The repository has no licence file, ships binaries only, and its release notes say the source archives do not contain ILASP's source | `github.com/ilaspltd/ILASP-releases` README and `v4.4.1` release body (GitHub API); `doc.ilasp.com` |
| FastLAS 2.2.0 | MIT ("Copyright (c) 2020 Imperial College London") | `github.com/spike-imperial/FastLAS` `LICENSE`; GitHub API `license.spdx_id` |
| clingo 5.8.2 (evaluator) | MIT; already installed and approved under IL1-D3 and IL1-D8 | IL1 spec §12 |

**Assessment.**
- **(a) ILASP:** its terms stop under IL-R5 for the owner's ruling.
  - **No registration or click-through:** the download is a public GitHub
    release asset.
  - **Not committed:** nothing is committed, and nothing is distributed.
- **(b) FastLAS:** MIT, which IL-R5 accepts without a ruling. Its container
  route also needs the Ubuntu image and the container's apt packages
  approved, with their licences recorded at the gate if (b) is chosen.

**What runs where.** The scratch prefix is `<scratchpad>/il2-live/`, outside
the repository, with no profile or PATH edits. Under (a):
1. Verify the size of the downloaded archive and record its SHA-256.
2. List its members, then extract it into `<scratch>/ilasp/`.
3. Run the probe (IL2-D4), then invocation 1.

If the archive holds more than the `ILASP` binary (for example a bundled
clingo), the member list and each member's licence notice are recorded before
the probe. If ILASP needs a `clingo` executable on `PATH`, a two-line
scratch shim calls the IL1 venv's `python -m clingo`. The shim is recorded,
and it adds no download.

## 13. Owner gate record (2026-10-27)

**The approved bytes.** The owner ruled in the session on 2026-10-27 over
spec r1, SHA-256 `fcf647b387f3a7fc22f9eb5da760008ab528a07ecf9c88d3581d9be885ffd7f6`
(commit `26c9a94`), which is sections 1–12.

**The owner's words (o):** "IL2-D1: ILASP 4.4.1. I rule that this use is
non-commercial research, so its terms are accepted. Approve the IL2-D2
download and the other IL2 decisions as proposed."

| ID | Ruling |
|---|---|
| IL2-D1 | **(a) ILASP 4.4.1 only**, target `ilasp`. The owner rules that this use is non-commercial research, so ILASP's terms are accepted under IL-R5. FastLAS is not used |
| IL2-D2 | **(a) approved:** the `ILASP-4.4.1-macOS-M1.tar.gz` release asset, 1,982,845 bytes, into a scratch prefix only. Its SHA-256 is computed and recorded at download, because upstream publishes none |
| IL2-D3 | as proposed: a learner timeout of 540 s if the probe's `ILASP --help` lists one, otherwise the wall clock alone, recorded as a deviation |
| IL2-D4 | as proposed: the toy-task format probe, before invocation 1 |
| IL2-D5 | as proposed: `#maxv(4)`, recall 2 per predicate and 1 per comparison, the default `#max_penalty` |
| IL2-D6 | as proposed: (a), the reader refuses `builtin-comparison` |
| IL2-D7 | as proposed: re-target IL1-Q2's halves to IL5 and IL4 |
| IL2-D8 | as proposed: the parser-only Popper canonical-name refusal, in IL2 |
| IL2-D9 | as proposed: (a), positional ids `e<i>` |
| IL2-D10 | as proposed: `claude/il2` from `main` at `65fd6df` |
| IL2-D11 | as proposed: corpus-first for the reader, prose for the rendering, no spec panel |
| IL2-Q1 | as proposed: carried to the ilp-learners close |

**No other approval.** No further run, install or amendment is approved
beyond these rulings.

## 14. Implementation findings (recorded as found)

**IL2-F1: a corpus case stopped before the check it was written for.**
- **The case:** corpus case `c4-type-confused` (T8) was the two-atom clause
  `wrong :- f_refund_amount(V1,V2), f_refund_by(V2,V3).`
- **What happened:** the fragment checker refused it at check 6,
  `non-ground-absence`, because neither atom has all its variables bound by
  the other. It never reached 9b.
- **The fix:** the case is now
  `wrong :- f_refund_amount(V1,V2), f_refund_by(V2,V3), f_refund_channel(V1,V3).`
  Its third atom is designated, so 9b names the join. This is the shape of
  IL1's join case J1.
- **Approval:** the corpus was written after the gate approved the
  instrument (IL2-D11). The owner had not read its bytes, and the case's
  meaning is unchanged: a type-confused join is refused by 9b.

**IL2-F2: two defects in the T1b harness.**
- **The split:** it split the task at the first `#pos(`, assuming the first
  example is positive. The refunds example's first week is labelled `neg`.
- **The mode regex:** its `[^)]*` stopped at the `)` of `var(t_refund)`.
- **The fix:** test-only. The split now matches `#pos(` or `#neg(`, and the
  regex counts `var(` occurrences.

**IL2-F3: the spec under-counted the moved RF1 goldens.**
- **The miss:** §6 listed 8 moved goldens. The CLI tree golden
  `tests/fixtures/rf1-pins/goldens/cli/tree.json` also records both `target`
  actions' choices and help, so **9 goldens move**.
- **How the tree was edited:** only those two actions were patched, by
  direct edit, as IK3 and IK5 edited the tree.
  - **Recapturing the tree is wrong:** a capture also writes the
    `--compiled-operations` successor, which `test_cli_tree` inserts at test
    time over RF1's historical bytes.
- **The other 8 files:** captured with `GND_RF1_CAPTURE` under Python 3.14,
  3.13 and 3.11. The three captures of each shared file were byte-identical.

**IL2-F4: the approved ILASP binary cannot start on this machine.**
- **The download (IL2-D2 (o)):** done.
  - The size, 1,982,845 bytes, matches the approved figure.
  - Its SHA-256, computed at download, is
    `7e9fd1ccbafa3241558c1f70a868b1c3e141de52dbdc76d26396b70f492cd75c`.
  - It is recorded with the member list in `evidence/IL2/download.json`.
- **The archive:**
  - It holds `ILASP`, a Mach-O arm64 executable, and three example tasks.
  - It also holds `ClingoLicense.txt`, which says clingo is statically linked
    and is MIT-licensed. Those terms cover clingo only.
- **The failure:**
  - **The link:** `otool -L` shows ILASP dynamically linked against
    `/opt/homebrew/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/Python`.
  - **The symbols:** ILASP imports 63 CPython C-API symbols, because it
    embeds Python (PyLASP).
  - **The machine:** it has no Python 3.10 framework.
  - **The result:** the probe's first command, `ILASP --version` under the
    bounded environment, ends with `dyld: Library not loaded`, exit 134
    (`evidence/IL2/probe/ilasp-version.txt`).
- **What has not happened:** no task was read, so this is neither the format
  probe's output nor a run of record.
- **What it blocks:** IL2-D4's probe and IL2-C4's live run. The gate approved
  no further download, and `brew install python@3.10` is a system package
  manager, which IL-R2 forbids.

### New decision surfaced by IL2-F4

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IL2-D12 | How to give ILASP the Python 3.10 it links against | **(a) A scratch Python 3.10 from python-build-standalone,** the same source uv uses: `https://github.com/astral-sh/python-build-standalone/releases/download/20260310/cpython-3.10.20+20260310-aarch64-apple-darwin-install_only_stripped.tar.gz`, 19,484,823 bytes, SHA-256 `83a95278567c1f5fea1e886684895c24f467e66f3e9ab3a20321402f54409d14` (from the release's `SHA256SUMS`). Licences: CPython PSF-2.0; the build scripts MPL-2.0. It is extracted into `<scratch>/py310/`. A scratch shim directory holds `Python.framework/Versions/3.10/Python` as a symlink to its `lib/libpython3.10.dylib`, and ILASP runs with `DYLD_FRAMEWORK_PATH=<scratch>/fw` and `PYTHONHOME=<scratch>/py310` in its explicit environment. No system path is touched. **Risk:** a non-framework build may differ from Homebrew's in ways ILASP notices; a load failure is recorded and stops again. **(b) ILASP's Ubuntu build in the podman VM,** which needs an Ubuntu image pinned by digest and the container's own Python 3.10; this costs more and adds a container. **(c) Stop IL2's live run,** recording IL2-C4 as not run, with the reason, as a refuted premise ("the macOS binary is self-contained") | (a) |

### Owner ruling on IL2-D12 (o), 2026-10-27

"IL2-D12 (a): approve the python-build-standalone CPython 3.10.20 download
(19,484,823 bytes, SHA-256 83a95278…9d14) into scratch with the
framework-path shim, then run the probe and invocation 1."

**The download:**
- **Checked:** it matched both the approved size and the SHA-256
  `83a95278567c1f5fea1e886684895c24f467e66f3e9ab3a20321402f54409d14`.
- **Its members:** every one sits under `python/`, a relative path.
- **Where it went:** extracted to `<scratch>/py310/`.

**The shim:** `<scratch>/fw/Python.framework/Versions/3.10/Python` is a
symlink to `<scratch>/py310/lib/libpython3.10.dylib`. ILASP runs with
`DYLD_FRAMEWORK_PATH=<scratch>/fw` and `PYTHONHOME=<scratch>/py310` in its
explicit environment. With them, `ILASP --version` prints the version line
`ILASP version 4.4.1 (release built on Nov 11 2024)`.

**IL2-F5: what the IL2-D4 probe recorded, and the corrections it forces
(written before invocation 1, as §6 requires).** The probe's files are in
`evidence/IL2/probe/`: the two toy tasks, their stdout and `ilasp-help.txt`.

- **The argv:**
  - `--version=4` is the documented flag. `--version` alone and `--help` are
    not options: ILASP prints its usage and exits 1.
  - **The argv is unchanged:** `ILASP --version=4 task.las`.
- **No learner timeout (IL2-D3 → (a)):** the help lists no timeout option.
  The 600 s wall clock is the only limit, so `learner-timeout` is
  unreachable. This is a deviation from IL-R9's learner-timeout clause, and
  IL2-D3 (a) as ruled accepts it.
- **Extraction is corrected.**
  - **What the probe showed:** ILASP 4.4.1 prints its `%%` timing block
    first and the hypothesis after it. §6's rule ("before the first line
    starting with `%%`") would return `""` on every run.
  - **The corrected rule:** the hypothesis is the first maximal run of
    `wrong … .` lines **after the last line starting with `%%`**.
    `UNSATISFIABLE` anywhere still means none.
  - **Pinned:** `test_extract_reads_the_hypothesis_after_the_timing_block`
    holds the correction to the probe's recorded output. Run over that
    output, the pre-fix extractor returns `''`.
- **UNSATISFIABLE still exits 0.** An unsatisfiable task is
  `termination: completed` with `import: none`.
- **The default search space includes constraints:** `-s` on the toy task
  lists `:- p(V1).` and the bare fact `wrong.` beside `wrong :- p(V1).`. The
  approved argv is kept unchanged, without `-nc`.
  - **What can follow:** a learned constraint is refused `asp-constraint`,
    and a learned `wrong.` is refused `empty-body`. Either is a recorded
    outcome, not a defect (plan §2).
  - **Changing the search space** would be a settings change, which needs an
    owner-recorded amendment (IL-R9).
