# Phase PL12: independent adversarial review

- Reviewer: one Claude subagent (same model family as the author)
- Date: 2026-10-14
- HEAD: ea035df0a57acc508afd4cae7c18fa730afab668, plus the uncommitted PL12 working tree
- `shasum -a 256 src/gnd/export/pyrel_rules.py`: `d9bc8ec7d3b248fde405301b421c13584faddfe6a848c81ec318004a9ebbdf3b`
- `shasum -a 256 tests/test_pyrel_rules.py`: `fe0b9d1a391a56a40399b56e5245b39e6f5b5cdadfa334705c25103657d417a5`
- Scratch (all probes, harness, mutants): `/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public/fd814110-b392-4c16-8294-2db75ff438c9/scratchpad/pl12/` (called `$S` below)
- Harness: `$S/harness.py MODEL POP` renders the duckdb program, runs it with the pinned interpreter, and compares it with `gnd.api.check(..., unredacted=True)`. It uses the same normalisation as `tests/test_pyrel_rules.py::_gnd`, and it also maps `unchecked`.

## Verdict: REVISE

On the 11 corpus populations the DuckDB program agrees with GND, and the test passes: 26/26, oracle lane included. It does not agree on new populations. Six blocking-class disagreements came out of eight new scratch models. In three of them the program reports a clean or vacuous result where GND reports an alethic failure. One is a crash on a supported construct (`!=`). The LQP `require` forms mean the same as the denials, which the PyRel source settles (see §2). The `--compile` claim of one `Require` per rule is false for multi-role uniqueness. The tests kill only 3 of 17 seeded mutants, and 2 of the survivors are equivalent.

## 1. Semantic disagreements with GND (DuckDB version)

### B1. Exit precedence: a later vacuous rule turns an alethic failure into exit 2 (blocking)
`src/gnd/export/pyrel_rules.py:473-490`. `exit_code = max(exit_code, 2)` runs after a violation has already set it to 1, so the program returns 2. Line 490, `return 1 if exit_code == 1 else exit_code`, is an identity: mutant M8, which replaces it with `return exit_code`, survives as an equivalent mutant. GND's band (`checker/_reports.py:140`) is 1 > 4 > 2 > 0. Whether the program returns 1 or 2 now depends on rule order.
Repro: `uv run python $S/harness.py $S/probe.orm.json $S/p2.population.json`
```
member#0  violated  [{"level": 1, "person": "p1", "team": "t1"}, {"level": 1, "person": "p1", "team": "t2"}]
...
lead_has_badge  vacuous  (no facts for it to apply to)
=== DISAGREE  program exit 2  gnd exit 1
```

### B2. The coverage "unknown" status is invented and hides violations (blocking)
`pyrel_rules.py:473-476`. Every family is marked `unknown` when any asserted fact type it reads is missing from `covers`. GND has no `unknown` verdict. Coverage omission applies only to `mandatory`/`mandatory-disjunctive`, and there it yields `vacuous` (`checker/_core.py:1011-1046`). Guarded atoms are closed-world "regardless of `covers`" (representation-format.md, guarded section).
Repro p3 (`team_badge` not covered): GND `lead_has_badge fail [{"$p":"p1","$t":"t1"}]` and exit 1. The program prints `lead_has_badge  unknown` and `tag_values  unknown`, and exits 2.
Repro p4 (`person_has_tag` not covered): GND gives `person_has_tag#0 vacuous`, with `tag_values` and `pid_values` passing. The program prints `unknown` for all three. The exit is 2 either way, but the statuses differ.

### B3. A guarded `!=` comparison crashes the export (blocking)
`pyrel_rules.py:38-39,343-344`. `_NEGATED["!="] == "=="`, but `_PYOP` has no key `"=="`, so `denial_text` raises `KeyError`. `_cmd_export_pyrel_rules` (`commands/export.py:40-62`) does not have the predecessor's catch-all `except Exception -> EXIT_INTERNAL`. The result is a raw traceback with exit 1. `!=` is one of the six documented operators. The LQP target renders, because only the denial path negates. No test uses `!=`.
Repro: `$S/disc.orm.json` with operator `!=` → `KeyError: '=='` at `pyrel_rules.py:344`, exit 1. The file now holds `=`; change it back to reproduce.

### B4. Object-type universes are narrower than GND's (blocking)
`_Model.plays` (`:111-120`) and `_universes` (`:392-407`) leave out two things that `universe._instance_values_of` includes:
- **(a) Subtypes.** GND adds the transitive subtype closure (`_descendant_closure`). `subtype_of` is not refused. A subtype with its own reference renders, but its roles are missing from the supertype universe.
  Repro: `$S/harness.py $S/sub.orm.json $S/sub.population.json`. GND gives `person_has_tag#0 fail ['m7']` and exit 1. The program prints `person_has_tag#0  OK` and exits 2. That is a false OK on a mandatory rule. With `inherits_reference: true`, the export refuses with "object type 'manager' has no primitive or reference value type", which does not name subtyping as the unsupported construct.
- **(b) Rosters of entities that denote a value type.** For a value type V, GND also collects the `instances:` rosters of every entity whose reference resolves to V (`_denoting_types`). The program adds only `instances[V]`.
  Repro p6: GND gives `pid_values fail ['zz','p9']`. The program prints only `pid_values violated "p9"`, missing `zz`, which comes from `instances.person`.

### B5. Bag semantics: duplicate rows are lost, and spanning uniqueness disappears silently (blocking)
`load()` uses `m.define`, which has set semantics, so duplicates are collapsed. `_uniqueness` returns `None` for spanning keys (`:228-229`). No comment is emitted and no header text mentions it. Spec §6.1 says "skipped with a comment", and D2 says "the header says so". Neither is implemented, and "one line per rule" is false because the rule simply vanishes. Non-spanning uniqueness also misses exact duplicate rows.
Repro: `$S/harness.py $S/span.orm.json $S/span.population.json`. GND gives `member#0 fail` (duplicate row), `lead#0 fail` (spanning) and exit 1. The program prints all OK and exits 0. `grep -n spanning` on the rendered program returns nothing.

### B6. Derived fact types are recomputed rather than read, so GND's derivation verdicts are lost (blocking for derived models)
`_relations` (`:429-431`) never loads population rows for derived fact types, and `_derivations` defines them instead. GND checks the population's claimed derived facts. Derivation verdicts feed the band (`derivation-not-covered` gives 4, a wrong claim gives 1), and guarded rules over an uncovered derived antecedent are `vacuous`. The agreement test runs no derived model: `complete` appears only in the compile test and the single-source test.
Repro: `$S/harness.py src/gnd/examples/bookrec/complete.orm.yaml src/gnd/examples/bookrec/seed.population.json`. The program prints 3 `all_eligible violated` lines and exits 1. GND gives `all_eligible vacuous` and exit 4.
Repro: `$S/complete-noderived.population.json` (claimed `book_is_eligible` emptied). The program exits 0. GND exits 1 on the derivation failure.

### H1. A disconnected guarded antecedent is cross-joined instead of refused (hardening, medium)
GND reports `unchecked` / `join-disconnected` with exit 4 (representation-format.md). The program cross-joins and reports a violation.
Repro: `$S/harness.py $S/disc.orm.json $S/disc.population.json`. The program prints `disc  violated {"$b":"z","$p":"p1","$t":"t1","$u":"t2"}` and exits 1. GND gives `('disc','unchecked','join-disconnected')` and exits 4. Unchecked outcomes in general (exit 4, `values-not-comparable`, `literal-type-ambiguous`) are never produced. This should be refused by name, or reported as unchecked.

### H2. Uniqueness witness shape is per key group, while GND gives one verdict with all offending facts (hardening, medium)
`witnesses()` (`_DUCKDB_MAIN`, `:502-512`) prints one line per key. GND emits one verdict that lists every offending fact. The violating facts are the same set, but the spec's "witnesses in GND's shape" claim and the test's normalisation (`_gnd` wraps all `offending_facts` in a single witness) fail as soon as two keys violate.
Repro p1: the program prints two `member#0 violated` lines. GND gives one verdict with four facts. The harness shows the `only program` / `only gnd` difference.

Agreements observed on the new probes: a multi-role subset whose superset fact type has an extra role (`lead_is_member`); guarded rules with a literal in the antecedent and in the consequent atom (`level3_leads_t1`); a comparison (`level_cap`); the violating set for uniqueness with two non-key roles; value widening through entity-typed roles (`p4` in `pid_values`); and mandatory with an empty fact list but a populated universe, which is vacuous on both sides (p5).

## 2. LQP `require` vs the DuckDB denial

Settled from PyRel 1.30.1 source:
- `semantics/backends/lqp/metamodel2flow/require_errors.py:73,118-123` builds `domain_items ∧ mm.Not(task=task.check) ∧ construct(Error)`. The whole check `Logical` sits under one `Not`, so a variable that appears only in the check is quantified inside it. `require(fact(x, String.ref()))` therefore means `¬∃y fact(x,y)` on violation. `--compile` confirms this, for example `domain Logical person_any(string) check Logical person_has_tag(string, string_2)`. Error attributes come only from domain vars (`VarFinder().find_vars(task.domain)`).
- `require(not_(atom))` becomes `Not(Logical(Not(atom)))`, which is the same as the denial `atom`. This is equivalent.
- Several `require` arguments are not one conjunctive check. The front end emits one `Require` per argument. Semantically, the union of `D ∧ ¬(a=b)` and `D ∧ ¬(c=d)` equals `D ∧ ¬(a=b ∧ c=d)`, so this matches `not_(a==b, c==d)`. But see H3.
- The legacy path (`semantics/backends/legacy_lqp/rewrite/transform_require.py`) also builds errors from domain vars plus the Require's own check. The non-`unique` equality pattern is not converted into an FD (`functional_dependencies.py` requires a `unique` lookup), so the requirement is checked rather than assumed. I did not find documentation, only source, so engine-side semantics stay engine-unverified.

### H3. `--compile` is false for multi-role uniqueness (hardening, medium)
`m.where(...).require(team_1 == team_2, level_1 == level_2)` compiles to two `Require` nodes, so `compile_only` prints `9 requirements compiled (8 rules in the model program)` and exits 1 (`:595-598`). Spec D3 and §8 row 2 ("exactly one Require per rule") are violated. The engine would also emit two errors for every violating pair. None of the four tested models has two non-key roles.
Repro: `tutorials/runtimes/.venv/bin/python -I $S/probe_lqp.py --compile; echo $?` prints that line and then 1.

## 3. Honesty

### H4. The headers and CLI help overstate what is verified (hardening, medium)
- **(a) D3 label missing.** D3 requires LQP execution to be labelled engine-unverified. The LQP header (`:617-624`) says the engine "enforces requirements and reports every violation", and the `--rules` help says "'lqp' enforces them with require on a RelationalAI engine". Neither says the path is unexercised. Only `docs/runtimes/pyrel.md` says so.
- **(b) Cited lowering is not the default pipeline.** The cited lowering (`require_errors.py`) belongs to the **`direct`** LQP compiler. The program sets `reasoners.logic.use_lqp=True` without `lqp.compiler`, and the default is `"legacy"` (`config/config_reasoners_fields.py:77-111`). The DuckDB header says a RelationalAI engine "compiles a requirement into exactly that query", but the evidence comes from a pipeline the program does not select.
- **(c) "Differ only in who enforces them" is overstated.** The DuckDB program adds vacuity, `unknown` and exit bands. The LQP program has none of them: an empty fact list gives no errors and exit 0. The LQP program also skips spanning uniqueness, like the DuckDB one (B5).
- **(d) Weak warning filter.** The LQP run path counts any warning whose text contains `require`, so "required" matches too. A warning such as a deprecation notice would be counted as a violation and give exit 1. UNREPRODUCED, since it needs an engine.
- **(e) Ignored flags.** With `--rules`, both `--connection` and `--duckdb-path` are accepted and silently ignored (`commands/export.py:111-112`).
- **(f) `--compile` is described accurately.** Its docstring calls `FrontCompiler`/`Walker` an "internal API, pinned version", and the docs say it checks well-formedness, not the rules. Both statements are fair. The docs page itself passes: `GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel` reports 16 blocks passed.

### H5. Standing rules 1 and 3 (validation before rendering) are not implemented (hardening, medium)
`render` (`:606-612`) parses the document with `_parse_document` and never calls `load_model`. As a result:
- A model that `gnd validate` rejects is exported with exit 0. In `$S/invalid.orm.json`, a guarded atom omits a role. The omitted role silently becomes an existential `Integer.ref()`/`String.ref()`, and `level_cap`'s witness loses `$t`.
- A constraint with no `modality` crashes the export with `KeyError: 'modality'` and a traceback.
The pre-existing checker export has the same gap, but the PL12 spec explicitly claims this behaviour.

### H6. Identifier collisions crash the generated program, and a crash exits 1 (hardening, medium)
`_RESERVED` (`:40-41`) does not include the generated locals `found`, `x`, `value`, `instances`, `population` or `config`.
- A fact type named `x` produces `TypeError: 'Ref' object is not callable` (`$S/names.*`).
- A fact type named `found` produces `found['member#0'] = ...` on a Relationship (`$S/names2.*`).
- Neither `main()` wraps `build()`, so the traceback exits **1**, which is the same code as an alethic violation.

## 4. Test strength: seeded mutants

These were applied by re-exec'ing the module from a pytest plugin (`$S/mutant_plugin.py`, `$S/mutants.py`). The full `tests/test_pyrel_rules.py` ran with the oracle lane each time. No repository file was edited.

| Mutant | Result |
|---|---|
| M1 `rows` unsorted | survived (harmless: comparison is set-based; order unasserted) |
| M2 guarded keeps only the first antecedent atom | killed |
| M3 `plays` drops reference widening | **survived** |
| M4 multi-pair uniqueness denial → conjunction of `!=` (wrong) | **survived** |
| M5 guarded vacuity any→all | **survived** |
| M6 mandatory never vacuous | **survived** |
| M7 universes drop the `instances` roster | **survived** |
| M8 `return exit_code` | survived (equivalent: proves line 490 is a no-op, see B1) |
| M9 subset vacuity all→any | **survived** |
| M10 uniqueness witness from `_1` only | survived (equivalent: the denial yields both orderings) |
| M11 universe uses only the first role played | **survived** |
| M12 coverage/unknown disabled | **survived** |
| M13 guarded vacuity includes derived facts | **survived** |
| M14 deontic hits set exit 1 | killed |
| M15 subset superset sequence reversed | **survived** (no multi-role subset in corpus) |
| M16 single-pair uniqueness `!=`→`==` | killed |
| M17 uniqueness checks only the first non-key role | **survived** |

Missing cases include:
- multi-role subset;
- uniqueness with two or more non-key roles and two or more violating keys;
- a value constraint on a reference value type, including an entity roster;
- a mandatory universe reached only through `instances`;
- vacuity for each family (empty sub vs empty sup);
- coverage omission per family;
- the `!=` operator;
- duplicate rows;
- a derived model in the agreement test;
- exit precedence with violation and vacuous together;
- the LQP compile test on a multi-non-key uniqueness model.

The corpus-only agreement oracle does not exercise most of the declared branches.

## 5. Goldens and pins

These look legitimate.
- Only the six `gnd_export_pyrel` help and exit goldens and `cli/tree.json` changed. The diffs are exactly the added `[--rules {duckdb,lqp}]` usage and help text, plus one tree action.
- Every line of `goldens.sha256` verifies: run in `tests/fixtures/rf1-pins/goldens`, `shasum -a 256 -c ../goldens.sha256` has 0 failures.
- `shasum` of the manifest is `519da6a1…227e`, which equals the new `MANIFEST_SHA256`. Per `tests/test_rf1_pin_harness.py:28` ("changing any golden edits this line too (SM1)"), updating it is the intended procedure.
- Not taking the unrelated drift from a fresh capture was correct.
- The pin and layering run produced 4 failures:
  - `test_rf1_pin_harness::test_mutation_table_rows_of_their_own`
  - `test_rf4_peripheral` (2)
  - `test_rf7_structure::test_complete_routing_and_dirty_controls`
  The same 4 nodes also fail when run against a clean HEAD worktree (`PYTHONPATH=<wt>/src`), so they predate PL12. With PL12 applied, the full selection gave 1460 passed and 4 failed.

## 6. Layering

No violation found.
- `tests/test_gnd_arch.py`, `test_rf1_layering.py`, `test_rf5_commands.py`, `test_rf8_structure.py` and `test_public_dependency_boundaries.py` pass.
- `gnd.export.pyrel_rules` is registered as lane `export`.
- `emit.render_pyrel_rules` imports lazily, and `commands/export.py` imports only `emit` and `pyrel_runtime`, as the predecessor command does.
- Nit: `pyrel_rules` imports the private `pyrel_runtime._parse_document` (same lane).
- Nit: the module is 680 lines against the spec's ~400.

## Required before approval
1. Fix the band precedence (B1). Remove `unknown`, and apply GND's coverage rule only to mandatory, as `vacuous` (B2).
2. Add `"==": "=="` to `_PYOP`, or map `!=`'s negation to `=`. Add the predecessor's catch-all to `_cmd_export_pyrel_rules` (B3).
3. Either implement GND's universe (subtype closure, denoting-entity rosters) or refuse `subtype_of` and value constraints or mandatory roles on reference value types by name (B4).
4. Either load facts with bag semantics or refuse duplicate rows at read time. Emit the promised spanning-uniqueness comment and header line (B5).
5. Either read claimed derived facts and report derivation status as GND does, or refuse derived models in the DuckDB target and say so (B6). Refuse disconnected antecedents (H1).
6. Shape uniqueness witnesses as GND does (H2). Make `--compile` count one rule per requirement or emit a single check (H3).
7. Add the engine-unverified label to the LQP header and the `--rules` help. Name the legacy/direct compiler choice. Tighten the warning filter (H4).
8. Run `load_model` first (H5). Reserve the generated locals and map program crashes to a non-1 exit (H6).
9. Add tests that kill M3–M7, M9, M11–M13, M15 and M17.
