# IL4 — AMIE-style miner

## 1. Status

**r1, approved by the owner 2026-10-28 (§13).** `auto=false`. Upstream
facts come from read-only GitHub metadata and pages (§12).

**Base:** drafted on `claude/il4`, branched from `claude/il3` at `732dd1f`
(PR #60, not yet merged). IL4 shares the registry, the CLI choices, the
schema enums, `ilp-bridge.md` and the RF1 goldens with IL3. Its
implementation starts only after PR #60 merges, from `main` (IL4-D13).

**What the gate decides:**
- IL4-D1 to IL4-D3: the miner, its download, and its licence under IL-R5;
- IL4-D4: the input of the run of record, which the refunds example cannot
  carry alone (§2);
- IL4-D5 to IL4-D12: the command shape, the mapping, the counting, the
  carry-overs, the probe, the settings and the approval instrument.

## 2. Provenance

- **Plan:** [ilp-learners-plan.md](ilp-learners-plan.md) r3 (SHA-256
  `329449d8…6281`, owner-approved in [`001-plan-gate.md`](../001-plan-gate.md)).
  The sections used:
  - §0;
  - §1 completion predicate 4;
  - §2 "AMIE-style miner (IL4)" and the registry's `contract` field;
  - §3, §4 IL4 (C1–C5), §5 to §7;
  - §9's IL4 row and its sweep rows (`manifest_sha256`, `--labels`);
  - §10 (D11 (o): holds only).
- **Prior phases:**
  - [`002-phase-IL1.md`](../002-phase-IL1.md): IL1-Q1 (the infix comparison
    in check 9b) is targeted at IL4;
  - [`003-phase-IL2.md`](../003-phase-IL2.md): IL2-D7 re-targeted IL1-Q2's
    `contract` half to IL4;
  - [`005-phase-IL3.md`](../005-phase-IL3.md): the shared live helper
    (`evidence/live_common.py`), IL3-Q2 (the private `_threshold_rows`), and
    the lesson that a moved RF1 golden moves its manifest line too.
- **Source inspected at `732dd1f`** (a read-only harvest, spot-checked):
  - **populations:** `gnd.population.load_population` (`population.py:518`).
    `covers` lists "the fact-type ids the population claims completeness for"
    (`gnd-orm-core` population-format reference, line 47);
  - **`gnd discover`:** the population digest is the SHA-256 of the
    population file's bytes (`discover/service.py:220`). A candidate holds
    only when the checker passes it with zero violations (`:251-257`); a
    candidate with no subjects is `vacuous` (`:213-216`). Its provenance block
    is `discover/output.py:40` `induced(...)`: `inducer`, `method`,
    `manifest_sha256` (the population digest), `examples`, `support`,
    `counterexamples`, `evidence`;
  - **guarded constraints:** `schema/orm-meta.schema.json:1699`. An `atom`
    consequent is `{fact_type, bind}`, as in
    `tests/fixtures/guarded/models/deontic.orm.yaml:41-50`;
  - **the join check:** `ilp_rewrite.check_join_types(atoms, compares, index,
    neutral, *, closures)` (`:66`), exported, called once;
  - **the export:** `--labels` is `required=True`
    (`commands/export.py:106`), and `ilp_service._prepare` loads the manifest
    unconditionally (`:135-160`);
  - **the import:** `gnd import ilp-rules` is registered in
    `commands/checking.py` `_register_import` (`:406-467`) and dispatched at
    `:668-675`. `tools/gnd_entrypoints.json:289-291` binds
    `gnd.commands.checking` to `gnd.export.ilp_service` only;
  - **the proposal:** built by `gnd.discover.output.proposal(...)`, as the
    ILP import does (`ilp_service.py:420-428`).
- **The refunds example, observed:** 8 populations of 2 or 3 refunds each,
  with 3 binary fact types (`refund_by`, `refund_amount`,
  `refund_channel`), all keyed by the refund. **Consequence:** any closed
  rule without constants needs at least 4 atoms (for example "refunds by the
  same customer share a channel"), beyond AMIE's default of 3. A rule with
  constants is possible, but over 2 or 3 refunds it is noise. This is why
  IL4-D4 exists.

## 3. Obligations — inline harvest

| Obligation | Source | Discharged in |
|---|---|---|
| `gnd export ilp --target amie MODEL --population POP --out DIR`: an unlabelled export of one population as typed binary relations; other arities skipped and listed | completion 4; §2; IL4-C1 | §6 export; T1 |
| `--labels`/`--population` mutually exclusive by target, enforced post-parse with exit 64; the `popper`/`neutral` missing-`--labels` exit unchanged; two moved RF1 goldens listed | §2; IL4-C5 | §6 CLI; T7 |
| `gnd import mined-rules MODEL RULES --population POP --reported FILE --target amie --out PROPOSAL`, in `gnd.commands.checking`, with its own report schema and new RF1 goldens | §2; §5 | §6 import; T8, T11 |
| A mined rule maps to a schema-valid `guarded` constraint with an `atom` consequent; constants, recursion and non-binary atoms per the spec's table, each with a test | IL4-C2 | §6 mapping table; T3 |
| GND counts numerator and denominator over distinct head pairs and matches a brute-force oracle | IL4-C3; §2 "Counting" | §6 counting; T4 |
| `support-mismatch`, `covers-nothing`, `open-world-head`, `type-confused-join` (through the shared function) and the refusal of a rule that does not hold, each with a test | IL4-C3 | T5 |
| Holds only (D11 (o)); all-or-nothing (D10 (o), IL-R11) | §10 | §6 admission; T5, T6 |
| Provenance: `examples` are opaque fact ids, `manifest_sha256` the population digest, as `gnd discover` writes it | §2 | §6 provenance; T6 |
| One live run under IL-R9, with JVM and miner versions, and a replay test | IL4-C4 | §6 live run; T9 |
| The registry's `contract` field takes `unlabelled-horn`; `amie` is export-only for `gnd export ilp` | §2 registry | §6 registry; T2 |
| IL1-Q1: should an infix comparison take part in check 9b? | IL1 record | IL4-D9 |
| IL1-Q2 (the `contract` half) | IL2-D7 | the `amie` entry is the first `unlabelled-horn` contract (§6) |
| New schemas in the inventories; RF6 census delta; layer map | plan §5; IL3-F4 | T12; §6 |
| A section of `ilp-bridge.md` | plan §5 | §6 docs; T13 |
| IL-R1 to IL-R11 and IK-R1 to IK-R12 | plan §0 | §4 |

## 4. Rules bound to IL4

**Standing rules.**

| Rule | Binding |
|---|---|
| 1 Totality | **New reader:** `ilp_amie.parse_rules`, closed over AMIE's rule-line grammar (§6). **Caps:** 1 MiB of text, 256 rules, 4 atoms per rule (3 body + head), variables `?[a-z]`, relation names from the export only, counts of at most 18 digits. Every input outside the grammar exits 3 `unparsable` with its line; never a traceback. |
| 2 Algorithm bound | **The export** is linear in facts. **The counting** is a join over at most 3 body atoms: its work is bounded by the product of the body relations' sizes, capped by `MAX_JOIN_ROWS` (IL4-D7) and refused `too-large` before it runs. |
| 3 Validation order | Reader refusals, then the mapping's refusals (§6 table), then `type-confused-join`, then the counts, then the holds check, then the checker. |
| 4 One walk | **One registry.** **One join-type check** (`check_join_types`, called directly). **One proposal builder** (`discover.output.proposal`). **One counting definition**, shared by the import and the oracle test's spec, not its code. |
| 5 One home | `ilp-bridge.md` gains an AMIE section: the export, the mapping table, the counting definitions and the refusal names. |
| 6 Measurement | IL4-C1 by golden bytes under two hash seeds; IL4-C3 by an oracle written in the test; IL4-C4 by a replay test. |

**Plan rules (IL-R).**

| Rule | Binding |
|---|---|
| IL-R1 | No AMIE or JVM dependency; IL1's T7 already names `amie`. |
| IL-R2 | **The script** is `evidence/IL4/run_amie.py`, using `evidence/live_common.py`. **The JVM** is the already-installed Homebrew OpenJDK 21.0.10 (`/opt/homebrew/bin/java`), used read-only. **The download:** the AMIE jar only, into a scratch prefix. |
| IL-R3 | IL4's sibling contract (`unlabelled-horn`) shares the registry, the join-type check and the proposal builder; it does not copy the `wrong/1` rewriting. |
| IL-R4 | AMIE's printed counts are the claim. GND counts itself and compares. The PCA confidence is kept verbatim and never compared or written into provenance. |
| IL-R5 | AMIE is CC-BY-4.0 and bundles Javatools (CC-BY-3.0): not OSI licences, so they stop for a ruling (IL4-D3). |
| IL-R6 | AMIE's stdout is untrusted; only the extracted rule lines reach the capped reader. |
| IL-R7 | No wire version changes. `amie` widens `ilp.schema.json`'s `target` enum only; `ilp-import.schema.json` is unchanged (`amie` is not a `labelled-clauses` target). |
| IL-R8 | The live input is a committed synthetic fixture under `tests/fixtures/ilp_learners/il4/`, named here (IL4-D4), or the refunds example, with the population digest recorded. |
| IL-R9 | §6 "Live run" fixes the outcome fields, the extractor, the settings, the argv, all six `ProcessLimits` and the fixed import arguments. AMIE's own timeout: IL4-D11. |
| IL-R10 | `live_common.Sanitizer`; IL1's T8 scan covers `evidence/IL4/`. |
| IL-R11 | Any refusal refuses the whole import. |

**Inherited rules (IK-R).** As IL3 (§4 of its spec), with these changes:
- **IK-R1:** admission adds no path: the proposal goes through
  `gnd evolve`, as `induced`/`proposed`/`deontic`.
- **IK-R7:** `gnd.export.ilp_amie` is assigned to the `export` lane in
  `tools/gnd_layers.json` before use. The command handler lives in
  `ilp_service`, so no new entry-point binding is needed.
- **IK-R11:** examples are opaque fact ids, never raw values.

## 5. Goal

**Export.** `gnd export ilp --target amie MODEL --population POP --out DIR`
writes `export.json` and `amie/facts.tsv`, byte-identical under two hash
seeds. Every other target's output is unchanged.

**Import.** `gnd import mined-rules` reads AMIE's printed rules, maps each to
a `guarded` constraint with an `atom` consequent, counts each rule's support
and confidence over the population itself, and admits the set only if every
rule's count agrees with AMIE's and every rule holds.

**Live run.** One AMIE run over the IL4-D4 input records one `termination`
value and one `import` value, replayed by a default-gate test.

## 6. Design

### Registry entry

```python
"amie": Learner(target="amie", learner="amie", method="ilp-amie", exports=True,
                render=ilp_amie.render, parse=ilp_amie.parse_rules,
                contract="unlabelled-horn", adapter_version=ilp_amie.ADAPTER_VERSION)
```

`EXPORT_TARGETS` becomes `("popper", "neutral", "ilasp", "rules", "amie")`.
`IMPORT_TARGETS` is unchanged, because it lists `labelled-clauses` entries
only. A new tuple, `MINED_TARGETS = ("amie",)`, lists the `unlabelled-horn`
entries; `gnd import mined-rules --target` takes exactly that.

### Export: `amie/facts.tsv` (`src/gnd/export/ilp_amie.py`, new)

- **One relation per binary asserted fact type** in the population. The
  relation name is `f_<fact type id>`, as the neutral form names predicates.
- **Typed entities:** each value is spelled `<object type id>:<value>`, so a
  join between an amount and a refund id is impossible inside AMIE too. A
  string value is escaped: tab, newline and backslash as `\t`, `\n`, `\\`.
  A value that cannot be spelled (a control character other than those) is
  refused `unrepresentable`.
- **One line per fact:** `subject TAB relation TAB object`, sorted.
- **Skipped:** fact types of other arities, derived fact types and fact
  types not in the population's `covers`. Each is listed in `export.json`
  under `skipped`, with its reason.
- **No labels.** `export.json` records the population digest as
  `population_sha256`, and no manifest.

### CLI (IL4-C5)

- **Export:** `--labels` loses `required=True`; a new `--population`
  joins it. A post-parse check in `commands/export.py` exits 64 when:
  - the target is `amie` and `--population` is missing, or `--labels` is
    given;
  - the target is any other and `--labels` is missing (the same message
    argparse printed before), or `--population` is given.
- **Moved RF1 goldens:** the `gnd export ilp` help usage line and its
  `unknown_flag` exit stderr ("required: …"), per Python version (IL3 split
  them), plus the choices in help, exit and `cli/tree.json`. Their manifest
  lines move with them.
- **Import:** `gnd import mined-rules MODEL RULES --population POP
  --reported FILE --target amie --out PROPOSAL [--actor ID] [--requested-at
  TIME] [--format text|json]`, registered in `_register_import` beside
  `ilp-rules`. Its handler, `_cmd_import_mined_rules`, lives in
  `ilp_service` and calls `ilp_amie`. New RF1 goldens: its help and exit
  probes.

### Reader: `parse_rules(text)` (closed, capped, total)

AMIE prints one rule per line after a header line, with tab-separated
columns: the rule, then head coverage, standard confidence, PCA confidence,
positive examples, body size, PCA body size and the functional variable. The
rule is `?a  r1  ?b  ?b  r2  ?c   => ?a  r3  ?c`: whitespace-separated
triples, then `=>`, then one head triple.

**The probe (IL4-D10) confirms this layout on the installed jar before the
reader is final.** The reader keeps the rule, the positive examples and the
body size; the other figures are kept verbatim as AMIE's claim.

### Mapping: a mined rule to a guarded constraint

`B1 ∧ … ∧ Bn ⇒ r(x, y)` becomes:

```yaml
type: guarded
antecedent: [ {fact_type: <B1>, bind: {<role>: "$x", <role>: "$z"}}, … ]
consequent:
  atom: {fact_type: <r>, bind: {<role>: "$x", <role>: "$y"}}
```

| Mined shape | Result |
|---|---|
| binary atoms over variables, every variable typed consistently | the constraint above |
| an atom whose subject and object are the same variable (`?a r ?a`) | refused `reflexive-atom` |
| a constant in an atom (only with `-const`, which IL4-D11 does not set) | refused `constant-atom` |
| the head relation also in the body (recursion) | refused `recursion` |
| a relation the export does not name | refused `unknown-predicate` |
| a variable bound to roles of incompatible object types | refused `type-confused-join` by `check_join_types`, called directly |
| a head variable absent from the body | refused `unbound-head` (AMIE's closed rules never print one; the reader still refuses it) |

### Counting (plan §2, IL4-C3)

- **Numerator:** the distinct head pairs `(x, y)` for which some binding of
  the other variables satisfies the body and the head holds in the
  population.
- **Denominator:** the distinct `(x, y)` for which some binding satisfies
  the body.
- **Confidence:** numerator / denominator, written with formula
  `std-confidence-head-pairs`.
- **The comparison:** AMIE's "positive examples" must equal the numerator,
  else `support-mismatch`. AMIE's "body size" is compared with the
  denominator and recorded; a disagreement there is reported, not refused,
  because the plan compares positive examples only.
- **A denominator of zero** is refused `covers-nothing`.
- **The work bound:** `MAX_JOIN_ROWS` (IL4-D7), refused `too-large` before
  the join.

### Admission (D11 (o))

- **Holds only:** numerator equals denominator. A rule that does not hold is
  refused `does-not-hold`, naming its counts.
- **Open world:** a rule whose head fact type is not in the population's
  `covers` is refused `open-world-head`.
- **Provenance**, as `gnd discover` writes it: `inducer` (`amie`, version),
  `method` `ilp-amie`, `manifest_sha256` the population digest, `examples`
  (opaque fact ids of the satisfied head facts, at most 256), `support` (the
  counts), `counterexamples` (empty, since only holding rules are admitted),
  `evidence` (the population's reference and digest).
- **Report:** `gnd-mined-import/1`, a new schema
  `src/gnd/mined-import.schema.json`, with `command` `import mined-rules`.

### Docs

`ilp-bridge.md` gains an "AMIE-style miner" section: the export, the CLI
rules, the mapping table, the counting definitions and every refusal name.
T13 checks it against the code's tables.

### Live run (`evidence/IL4/run_amie.py`, evidence only)

| Item | Value |
|---|---|
| Input | IL4-D4; the population digest recorded |
| Miner | AMIE 4.0.0, `<scratch>/amie4.0.0.jar` |
| JVM | `/opt/homebrew/bin/java` (OpenJDK 21.0.10), its version line recorded |
| argv | `java -Xmx2G -jar amie4.0.0.jar -maxad 3 amie/facts.tsv`, from the export directory; `-mins`, `-minhc` and `-minpca` per IL4-D11 |
| `ProcessLimits` | as IL3: 600 s, grace 10 s, stdin 0, stdout 16 MiB, stderr 4 MiB, total 20 MiB |
| Environment | `live_common.environment`, with `JAVA_HOME` set to the Homebrew JDK |
| Extraction | `ilp_amie.extract_rules`, shared with T9 |
| Import | `import mined-rules model.orm.yaml rules.txt --population population.yaml --reported reported.json --target amie --out proposal.json --actor ilp-live --requested-at 2026-01-01T00:00:00Z --format json` |

**The outcome:** `termination` as `live_common.termination`; `import`
`none` (no rule line), `refused:<name>` (exit 3) or `admitted`.

**Expected result, stated before the run:** depends on IL4-D4. On the
fixture, the planted rule should be mined and admitted; the planted
near-miss either is not mined (below AMIE's thresholds) or is refused
`does-not-hold`, which refuses the whole set (all-or-nothing). Either is a
recorded result.

## 7. Decisions

| ID | Decision | Options and cost | Proposed |
|---|---|---|---|
| IL4-D1 | The miner | **(a) AMIE 4.0.0** (`dig-team/AMIE`, released 2026-06-24), whose release publishes a SHA-256. **(b) AMIE 3.5.1** (2024), which publishes none. **(c) A small miner written for the evidence script**, which is not "a named rule-set learner" and would test GND against itself | (a) |
| IL4-D2 | The download (IL-R2) | `https://github.com/dig-team/AMIE/releases/download/v4.0.0/amie4.0.0.jar`, 96,104,317 bytes, SHA-256 `bbf65ef5b54f896a7c6d05e3faeaf5b58262e3828e61ae6dc3f3c71c932b8485` (the GitHub asset digest), checked before use. **No JVM download:** the Homebrew OpenJDK 21.0.10 already installed is used, read-only | as stated |
| IL4-D3 | The licence (IL-R5) | AMIE is CC-BY-4.0 and its Javatools CC-BY-3.0: attribution licences, not OSI. **(a) Accept:** nothing is committed or distributed, and the record attributes both. **(b) Decline:** IL4-C4 is not run | (a) |
| IL4-D4 | The run's input | The refunds populations hold 2 or 3 refunds each, all relations keyed by the refund, so AMIE (3 atoms, no constants) can find no closed rule. **(a) A synthetic fixture** `tests/fixtures/ilp_learners/il4/`: a small model (staff, teams, sites) with about 30 entities, one planted rule that holds (`works_in(x,t) ∧ team_site(t,s) ⇒ based_at(x,s)`) and one near-miss. IL6's AMIE row then uses this fixture, which differs from the plan's "refunds through every adapter": a plan repair at close. **(b) One refunds population** (the largest, 3 refunds): the run will almost certainly print no rule, `import: none`. **(c) Both,** the fixture as the run of record and refunds as a recorded second invocation, which needs this ruling to count as approved | (a) |
| IL4-D5 | Entity spelling | **(a) `<object type id>:<value>`**, so the export keeps types apart. **(b) Bare values,** which lets AMIE join a refund id with an equal amount | (a) |
| IL4-D6 | The import report | **(a) A new schema, `gnd-mined-import/1`.** **(b) Widen `gnd-ilp-import/1`,** whose `clauses` and `export_sha256` do not fit an unlabelled import | (a) |
| IL4-D7 | Bounds | 256 rules; 4 atoms per rule; `MAX_JOIN_ROWS = 1,000,000` per rule. The fixture's largest join is under 1,000 rows | as stated |
| IL4-D8 | Body-size disagreement | **(a) Recorded, not refused:** the plan compares positive examples only. **(b) Refused `support-mismatch` too** | (a) |
| IL4-D9 | IL1-Q1: infix comparisons in 9b | AMIE rules carry no comparisons, so IL4 cannot exercise it. **(a) Re-target IL1-Q1 to close,** with that reason. **(b) Change 9b now** without a case that reaches it, which the shipment rule forbids | (a) |
| IL4-D10 | The format probe | Before invocation 1, AMIE runs once on a toy TSV written here: `a:1 r a:2`, `a:2 r a:3`, `a:1 s a:2`, `a:2 s a:3` (so `r ⇒ s` and `s ⇒ r` hold). It records `-h`, the version banner and the output layout, and confirms or corrects `parse_rules` and the argv. Not the run of record | probe |
| IL4-D11 | Settings | `-maxad 3`, no `-const`, AMIE's default thresholds except `-mins 1` (support at least one pair), so a small fixture's rules are not filtered out. AMIE has no timeout option known to this spec; if `-h` lists one at the probe, use 540 s, else the wall clock alone (`learner-timeout` unreachable, as IL2-Q4) | as stated |
| IL4-D12 | Approval instrument | **Corpus-first** for the reader and the mapping (a serialized format): the T3 and T5 cases with their expected constraints or refusal names, committed before the code, the harness landing red. **Prose plus golden** for the export. **An oracle** for the counts. No spec panel | as stated |
| IL4-D13 | Base and branch | Implementation on `claude/il4` from `main` after PR #60 merges; this draft is committed on `claude/il4` from `claude/il3` | as stated |

## 8. Tests

New file: `tests/test_ilp_amie.py`. Corpus: `tests/fixtures/ilp_learners/il4/`.

| ID | Case | Expected |
|---|---|---|
| T1 | `gnd export ilp --target amie` over the fixture and one refunds population, under `PYTHONHASHSEED=0` and `1` | `facts.tsv` and `export.json` equal the goldens; seeds identical; `skipped` lists every non-binary or uncovered fact type |
| T2 | registry: `EXPORT_TARGETS`, `IMPORT_TARGETS` (unchanged), `MINED_TARGETS`; both choices; the export enum | pass |
| T3 | the mapping corpus: one case per row of the mapping table | the committed constraint, or exit 3 with the row's name |
| T4 | counting: numerator, denominator and confidence equal a brute-force oracle written in the test, over the fixture and randomized small populations | pass |
| T5 | `support-mismatch`, `covers-nothing`, `open-world-head`, `type-confused-join`, `does-not-hold` | exit 3 with that name, nothing written |
| T6 | an admitted rule: the proposal validates; provenance as §6; `gnd evolve preview` accepts it | pass |
| T6b | all-or-nothing: one holding rule and one refused rule | exit 3, no proposal |
| T7 | the post-parse checks of §6 "CLI", each case | exit 64; `popper` and `neutral` without `--labels` give the same stderr as before |
| T8 | `gnd import mined-rules` report validates against `mined-import.schema.json` | pass |
| T9 | replay of `evidence/IL4/live/invocation-N/`, using the script's constants, as IL3's T9 | pass |
| T10 | totality: over 1 MiB, 257 rules, a 5-atom rule, a malformed triple, a 19-digit count, a non-UTF-8 byte | exit 3 `unparsable`, never a traceback |
| T11 | RF1 pins and manifest under Python 3.11, 3.13 and 3.14 | pass |
| T12 | schema inventories list `mined-import.schema.json`; RF6 census delta; layer map | pass |
| T13 | the `ilp-bridge.md` AMIE section against the code's tables | pass |
| T-live | the scratch AMIE over the committed `facts.tsv` reproduces the committed rule lines, or, if AMIE proves not deterministic (as RIPPER did), the counts of the committed rules | pass |

**Gate command:** IL3's gate file list plus `tests/test_ilp_amie.py`.

## 9. Out of scope for this phase

- every adapter other than `amie`; IL6's walk and comparison table;
- rules with constants (`-const`), rules longer than 3 atoms, and rules that
  do not hold (D11 (o));
- PCA confidence as a GND figure;
- a GND command that runs a learner (D3 (a));
- any wire version change.

## 10. Size

Estimate: ~300 source lines (export, reader, mapping, counting, the import
handler, the CLI checks, the registry); ~420 test lines plus the corpus and
fixture; ~150 lines of run script; ~70 lines of docs.

## 11. Approval instrument

IL4-D12.

## 12. Licences and downloads (IL-R5, recorded 2026-10-28, before any download)

| Component | Licence | Source |
|---|---|---|
| AMIE 4.0.0 | CC-BY-4.0 ("AMIE is licensed under a Creative Commons Attribution 4.0 International License"), not OSI | `github.com/dig-team/AMIE` `LICENSE.txt` and README "Licensing" (read 2026-10-28); GitHub `license.spdx_id` `NOASSERTION` |
| Javatools (inside the jar) | CC-BY-3.0, not OSI | AMIE README "Licensing" |
| OpenJDK 21.0.10 | GPL-2.0 with the Classpath Exception; already installed by Homebrew, used read-only, no download | `java -version` |

| File | Bytes | SHA-256 |
|---|---|---|
| `amie4.0.0.jar` | 96,104,317 | `bbf65ef5b54f896a7c6d05e3faeaf5b58262e3828e61ae6dc3f3c71c932b8485` (GitHub asset digest) |

No registration or click-through step exists. Nothing is committed.

## 13. Owner gate record (2026-10-28)

**The owner's words (o):** "go with your recs", answering "Merge PR 60 and
approve IL4-D1 to IL4-D13 as proposed?" after the recommendation of (a)
AMIE 4.0.0, (a) accepting its CC-BY licences and (a) the synthetic fixture.

**Bound bytes:** r1 as committed in `374e225` (rebased from `302f36d`),
SHA-256 `e1dcb42f4a81a8f28eb8c128fa79b6dc83f607f12303fad6a57a7e5f94470648`.

| ID | Ruling |
|---|---|
| IL4-D1 | **(a): AMIE 4.0.0** |
| IL4-D2 | as proposed: the jar only, size and SHA-256 checked, into a scratch prefix; the installed OpenJDK used read-only |
| IL4-D3 | **(a): CC-BY-4.0 (AMIE) and CC-BY-3.0 (Javatools) accepted** under IL-R5; nothing committed; both attributed |
| IL4-D4 | **(a): the synthetic fixture** is the run's input; IL6's AMIE row uses it, a plan repair at close |
| IL4-D5 | as proposed: (a), `<object type id>:<value>` |
| IL4-D6 | as proposed: (a), `gnd-mined-import/1` |
| IL4-D7 | as proposed: 256 rules, 4 atoms, `MAX_JOIN_ROWS` 1,000,000 |
| IL4-D8 | as proposed: (a), body-size disagreement recorded, not refused |
| IL4-D9 | as proposed: (a), IL1-Q1 re-targeted to close |
| IL4-D10 | as proposed: the toy-TSV probe before invocation 1 |
| IL4-D11 | as proposed: `-maxad 3`, no `-const`, `-mins 1`, defaults otherwise |
| IL4-D12 | as proposed: corpus-first for the reader and the mapping, golden for the export, an oracle for the counts, no panel |
| IL4-D13 | as proposed, and done: PR #60 merged at `70266b5`; `claude/il4` rebased onto it |

**No other approval.** One run of record; a second run or a settings change
needs a further ruling.

## 14. Implementation findings (recorded as found)

- **IL4-F1 (premises, both hold).** T6's premise: a guarded constraint with
  an `atom` consequent over variables, built by `discover.output.proposal`,
  passes the checker (`pass`) and `gnd evolve preview` (exit 0) over the
  staffing fixture. The provenance premise: `PopulationView.fact_id` gives
  `ft<k>#<index>`, the ids `gnd discover` writes. No ruling changes.
- **IL4-F2 (spec gap: what `--reported` holds).** Neither the plan nor §6
  defines the run record. Implemented as `gnd-mined-run/1` (a `$defs` entry of
  `mined-import.schema.json`): the learner's name and version and the
  SHA-256s of RULES and of the population, mirroring `ilp-rules`' run
  record. Three input refusals follow, before the mapping:
  `learner-mismatch`, `rules-mismatch`, `population-mismatch`, each tested
  (T5). The learner's own figures stay in RULES, so the record carries no
  coverage.
- **IL4-F3 (spec text vs. a closed schema).** §6 puts `population_sha256`
  and `skipped` in `export.json`, but `gnd-ilp-export/1` is closed and IL-R7
  widens only its `target` enum. They live in `amie/relations.json`, which
  `export.json` binds by digest. No wire change.
- **IL4-F4 (the probe, IL4-D10, run on the toy TSV).** AMIE 4.0.0 has no `-h`:
  it exits 1 and prints its usage. It has no timeout option, so
  `learner-timeout` is unreachable (as IL2-Q4). Its rule lines have eight
  tab-separated fields and the count column is `Support` (§6 said "positive
  examples"). Without `-enstd` it computes neither standard confidence nor
  body size and prints `-2.000000` and `-1`: under the ruled argv the
  IL4-D8 body-size comparison is always "not reported". `-mins 1` switches
  the pruning metric to support; the `-minis` default (100) changed nothing
  on the toy, so the argv stands as ruled. AMIE runs 18 threads and prints
  rules as found, so their order is not stable (T-live compares sets), and
  it writes a `run-<timestamp>.csv` into its working directory.
- **IL4-F5 (check order between two rows).** A head relation outside
  `covers` is refused `open-world-head` before the `unknown-predicate` scan;
  a body relation outside `covers` is `unknown-predicate` (the export does not
  write it). Each has a case (m1, m3). Documented in `ilp-bridge.md`.
- **IL4-F6 (the oracle found a defect).** T4's randomized oracle found that
  `count` bound only the object of an atom whose two ends are one variable
  (`?b q ?b` counted 2 head pairs, not 1). The import never reaches it, since
  the mapping refuses `reflexive-atom` first; `count` is fixed so it is right
  on its own, and T4 is its regression.
- **IL4-F7 (moved RF1 goldens).** `gnd export ilp`'s help and exit goldens,
  split per Python version in IL3, are again identical under 3.11, 3.13 and
  3.14 (the new usage line wraps the same everywhere): the three files per lane
  become one `gnd_export_ilp.json`. Also moved: `gnd import`'s help and exit,
  `cli/tree.json`; new: `gnd import mined-rules`'s help and exit. Manifest
  rebuilt; `MANIFEST_SHA256` updated.
- **IL4-F8 (the expected result, stated before invocation 1).** The ruled
  argv filters on PCA confidence at 0.1 and on nothing else, so AMIE will print
  rules that do not hold on the fixture (for example `parks_at => based_at`,
  19 of 20). With all-or-nothing admission, the expected outcome is
  `termination: completed`, `import: refused:does-not-hold`. An admitted live
  result would need `-enstd -minc 1` (filter on standard confidence 1), a
  settings change that needs an owner ruling.

## Implementability notes (author, before the gate)

Two premises rest on the harvest, not on a run:
- **T6** assumes `gnd evolve preview` accepts a guarded constraint with an
  `atom` consequent built by `discover.output.proposal`. The schema allows
  it; no ILP import has written one yet.
- **The provenance's `examples`** assume a population fact has an opaque id
  as `gnd discover` writes it (`discover/output.py:40`).

Both are checked first at implementation. A failure is recorded as a finding
and, if it changes a ruling, returns to the owner.
