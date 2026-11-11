**Scope:** I reviewed only the supplied spec and diff, without running any tools. Code outside the diff (`baseline_key`, `atom_bind`, `variable_name`, `run_check`, the verdict enum, and `handle()` lines 1167–1273) is treated as opaque. Findings that depend on that code are marked as conditional.

## Findings

**1. Alignment drops variables shared by both editions, producing a false `standing` and exit 0 (high).**
`_guarded_projection` aligns only fact types that occur exactly once on each side. Any other variable is dropped from the key on both sides, even if both editions bind it. M2 allows only *unmatched added* variables to be projected away. The collision check in `keys` runs within each side only, so it doesn't catch this.
```python
I, A = "Imports", "InArea"
base = {"antecedent": [{"fact_type": I, "bind": {"src": "$s", "dst": "$t"}},
                       {"fact_type": A, "bind": {"component": "$s", "area": "$a"}}]}
head = {"antecedent": base["antecedent"] + [{"fact_type": I, "bind": {"src": "$t", "dst": "$u"}}]}
# Imports is now repeated on head, so only InArea aligns. Projection is ($a,$s); $t is dropped.
compare_editions([g("fail", [{"$s": "c1", "$t": "api", "$a": "core"}])],
                 [g("fail", [{"$s": "c1", "$t": "db", "$u": "x", "$a": "core"}])],
                 {"constraints[0]": base}, {"constraints[0]": head})
# -> standing [{c1→api}, {c1→db→x}], incomplete=False
```
Here `g` is `_verdict` with `constraint_type="guarded"`.
- **Fix:** drop a variable only if every one of its sites uses a fact type absent from the other edition. Otherwise return `None`.
- **Also check:** `variable_name(other.get(role))` when the head atom omits a role.

**2. Completeness is inferred only from `verdict == "unchecked"` (high).**
- `witness_rows` treats every verdict other than `fail`/`warning` as a decided empty set.
- An unknown verdict therefore yields a complete delta. This contradicts standing rule 1.
- A declared rule present in a model but missing from the verdicts becomes `added`/`removed`, not incomplete.
- The service never uses a side's `result.exit_code == 4`. A side-level incompleteness that isn't reflected in a row can still exit 0.

Reproduction: `compare_editions([_verdict("fail",[1])], [_verdict("anything-else")], {}, {})` returns `base_only [1]` and `incomplete=False`.

Fix:
- Accept only `{pass, vacuous}` as empty and `{fail, warning}` as findings. Mark anything else incomplete.
- Cross-check declared IDs in `constraints[side]` against the verdict addresses.

**3. A rowless failure against a rowed failure is compared without any shared key (medium).**
- M2 says a lack of a shared key makes the rule incomparable.
- For guarded rules, the `!= (None,)` guard skips projection and falls back to full keys.

Reproduction: `compare_editions([_verdict("fail",[1])], [_verdict("fail")], {}, {})` returns `base_only [1]`, `head_only [None]` and `incomplete=False`. Mixed rowless/rowed pairs should get a reason.

**4. Conditional: a missing POPULATION operand reaches I/O (medium).**
- Assumption: POPULATION is optional (`nargs="?"`), which the separate `--populations` arm suggests.
- In that case, `gnd check head.orm.yaml --baseline-model base.orm.yaml` loads both models and then calls `read_population_bytes(None)`. That call raises an uncaught error that probably isn't `PopulationLoadError`.
- `"population": None` also violates the schema's `type: string`.
- Rule 3 says this should be exit 64 before any I/O.

**5. Removing an ID gives a misleading exit 0 (low-medium, spec-level).**
Repro: `head = deepcopy(base); del head["constraints"][0]["id"]`. The result has:
- `constraint:local_imports [removed]` with 43 base-only findings;
- `constraints[0] [unpaired]` with a head `fail`;
- exit 0.

Text output reads as "43 fixed" even though the rule is unchanged. T2 sanctions this behaviour, but `added`/`removed` deltas look exactly like resolutions. Consider leaving removed/added rows without a directional delta, or adding a reason to them.

**6. Diagnostics and schema drift (low).**
- `test_invalid_population_bytes` pins `base-population-ill-formed` for the input `{`. A YAML syntax error doesn't depend on the model, so it should be `population-ill-formed` with side `null`.
- A row that lacks a projected variable is reported as `binding-projection-collision`.
- `{side}-check-refused` passes through whatever exit code `run_check` returns, which can fall outside the schema enum `[0,3,4,70]`.
- `issues[].path` and `rule_id` are typed as strings, but `refuse` copies attributes that may be `None`.
- Text output has no side label, so anonymous base and head rows with the same `constraints[i]` print identically.
- Text output omits modalities and standing bindings, despite T7's "same comparison".

## Claims that held up
- **Typed identity:** full and projected keys both go through `baseline_key`. `1 ≡ 1.0` and `True ≠ 1` are pinned. Projected values are ordered by sorted base name with the mapped head name, so positions match.
- **Single capture:** both admissions use the same `raw` bytes, and the read-once test is pinned. Caveat: this holds only if `load_population_bytes` resolves nothing through `source`.
- **Validation order:** conflicts, then models, then support, then vocabulary, then bytes, then admission, then evaluation, then comparison. Every refusal returns `rules: []`.
- **Budget:** rows, atoms and verdicts are all charged, and other work is linear in the charged verdict count. Exhaustion is all-or-nothing with exit 4. The module global is read at call time, so the monkeypatch test is genuine.
- **Fail-closed paths:** a one-to-one mapping conflict and a same-side collision both fail closed, and tests cover both.
- **Baseline compatibility:** the changes are additive, and the conflict branch is extended only when `--baseline-model` is set. The new schema branch has a `const` tag and `additionalProperties: false`, so it can't absorb existing reports. I couldn't see the 1167–1273 dispatch.
- **Decisive control:** 42 base-only, 0 head-only and 1 standing in both directions, with exit 0 when both bands are 1.

**Verdict: REVISE.** Findings 1 and 2 produce confident, complete exit-0 answers on inputs where the approved decision requires failing closed. Both are local fixes in `gnd/baseline.py`.
